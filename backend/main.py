"""FastAPI backend serving weather forecasts in the Open-Meteo response format.

Primary source: Open-Meteo (free, no key). Open-Meteo rate-limits per IP, and shared hosting
IPs (e.g. Render's free tier) are often blocked with HTTP 429. When that happens the backend
switches to MET Norway's Locationforecast API (free, no key) and converts its response to the
same format, so the frontend never sees the difference.
"""

import math
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
import tzfpy
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MET_NORWAY_URL = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
# MET Norway's terms require an identifying User-Agent.
USER_AGENT = "weather-forecast-app/1.0 github.com/PSubrat29/weather-forecast-app"

# Must stay in sync with FORECAST_PARAMS in frontend/src/lib/api.js
FORECAST_PARAMS = {
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,"
    "weather_code,surface_pressure,wind_speed_10m,wind_direction_10m",
    "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m",
    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
    "past_days": 7,
    "forecast_days": 7,
    "timezone": "auto",
}

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))
_cache: dict[tuple[float, float], tuple[float, dict]] = {}
# After a 429 from Open-Meteo, use MET Norway until this monotonic time.
_open_meteo_blocked_until = 0.0

app = FastAPI(title="Weather Forecast API")

# Comma-separated list of allowed origins; defaults to "*" so any frontend (GitHub Pages, localhost) works.
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"status": "ok", "endpoints": ["/weather?latitude=..&longitude=..", "/health"]}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    # Never calls external APIs, so it is safe to use as the hosting health check.
    # RENDER_GIT_COMMIT is set by Render; shows which commit is actually running.
    return {"status": "ok", "commit": os.getenv("RENDER_GIT_COMMIT", "local")[:7]}


@app.get("/weather")
async def weather(
    response: Response,
    latitude: float = Query(52.52, ge=-90, le=90),
    longitude: float = Query(13.41, ge=-180, le=180),
):
    """Return current conditions, hourly data and a daily forecast for the given coordinates."""
    key = (round(latitude, 2), round(longitude, 2))
    cached = _cache.get(key)
    if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    errors = []
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as client:
        for fetch in (_fetch_open_meteo, _fetch_met_norway):
            try:
                data = await fetch(client, *key)
            except Exception as exc:  # try the next source
                errors.append(f"{fetch.__name__.removeprefix('_fetch_')}: {exc}")
                continue
            if data is None:  # source skipped (rate-limit cooldown)
                continue
            _cache[key] = (time.monotonic(), data)
            if len(_cache) > 500:
                _cache.pop(next(iter(_cache)))
            return data

    if cached:
        response.headers["X-Data-Stale"] = "true"
        return cached[1]  # stale data beats no data
    raise HTTPException(status_code=502, detail="All weather sources failed: " + "; ".join(errors))


async def _fetch_open_meteo(client: httpx.AsyncClient, lat: float, lon: float) -> dict | None:
    global _open_meteo_blocked_until
    if time.monotonic() < _open_meteo_blocked_until:
        return None
    resp = await client.get(OPEN_METEO_URL, params={"latitude": lat, "longitude": lon, **FORECAST_PARAMS})
    if resp.status_code == 429:
        try:
            retry_after = max(int(resp.headers.get("retry-after", "")), 60)
        except ValueError:
            retry_after = 3600  # daily/hourly limits: don't keep hammering
        _open_meteo_blocked_until = time.monotonic() + retry_after
        raise RuntimeError("rate limited (429)")
    resp.raise_for_status()
    data = resp.json()
    data["source"] = "open-meteo"
    return data


async def _fetch_met_norway(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    resp = await client.get(MET_NORWAY_URL, params={"lat": lat, "lon": lon})
    resp.raise_for_status()
    return met_to_open_meteo(resp.json(), lat, lon)


# ---------------------------------------------------------------------------
# MET Norway -> Open-Meteo format conversion
# ---------------------------------------------------------------------------

# MET symbol codes (without _day/_night/_polartwilight suffix) -> WMO weather codes
_MET_SYMBOL_TO_WMO = {
    "clearsky": 0, "fair": 1, "partlycloudy": 2, "cloudy": 3, "fog": 45,
    "lightrain": 61, "rain": 63, "heavyrain": 65,
    "lightrainshowers": 80, "rainshowers": 81, "heavyrainshowers": 82,
    "lightsleet": 66, "sleet": 67, "heavysleet": 67,
    "lightsleetshowers": 66, "sleetshowers": 67, "heavysleetshowers": 67,
    "lightsnow": 71, "snow": 73, "heavysnow": 75,
    "lightsnowshowers": 85, "snowshowers": 85, "heavysnowshowers": 86,
}


def _symbol_to_wmo(symbol: str | None) -> int | None:
    if not symbol:
        return None
    base = symbol.split("_")[0]
    if "thunder" in base:
        return 95
    return _MET_SYMBOL_TO_WMO.get(base, 3)


def _apparent_temperature(temp_c: float, rh: float, wind_ms: float) -> float:
    """Australian BoM apparent temperature (no solar radiation term)."""
    vapour_pressure = rh / 100 * 6.105 * math.exp(17.27 * temp_c / (237.7 + temp_c))
    return round(temp_c + 0.33 * vapour_pressure - 0.70 * wind_ms - 4.00, 1)


def _local_zone(lat: float, lon: float) -> ZoneInfo:
    try:
        return ZoneInfo(tzfpy.get_tz(lon, lat) or "UTC")
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def met_to_open_meteo(met: dict, lat: float, lon: float) -> dict:
    series = met["properties"]["timeseries"]
    if not series:
        raise ValueError("empty forecast")
    tz = _local_zone(lat, lon)

    def local(ts: str) -> datetime:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz)

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M")

    hourly = {k: [] for k in ("time", "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m")}
    days: dict[str, dict] = defaultdict(lambda: {"tmax": -math.inf, "tmin": math.inf, "rain": 0.0, "prob": None, "codes": []})

    for entry in series:
        dt = local(entry["time"])
        data = entry["data"]
        inst = data["instant"]["details"]
        n1 = data.get("next_1_hours")
        n6 = data.get("next_6_hours")
        day = days[dt.strftime("%Y-%m-%d")]

        temp = inst.get("air_temperature")
        if temp is not None:
            day["tmax"] = max(day["tmax"], temp)
            day["tmin"] = min(day["tmin"], temp)

        # Hourly-resolution entries carry next_1_hours; later ones only next_6_hours.
        period = n1 or n6
        if period:
            details = period.get("details", {})
            day["rain"] += details.get("precipitation_amount", 0.0) or 0.0
            prob = details.get("probability_of_precipitation")
            if prob is not None:
                day["prob"] = max(day["prob"] or 0, prob)
            code = _symbol_to_wmo(period.get("summary", {}).get("symbol_code"))
            if code is not None:
                day["codes"].append(code)
        if n6 and not n1:
            d6 = n6.get("details", {})
            if d6.get("air_temperature_max") is not None:
                day["tmax"] = max(day["tmax"], d6["air_temperature_max"])
            if d6.get("air_temperature_min") is not None:
                day["tmin"] = min(day["tmin"], d6["air_temperature_min"])

        if n1:
            hourly["time"].append(fmt(dt))
            hourly["temperature_2m"].append(temp)
            hourly["relative_humidity_2m"].append(inst.get("relative_humidity"))
            hourly["surface_pressure"].append(inst.get("air_pressure_at_sea_level"))
            wind = inst.get("wind_speed")
            hourly["wind_speed_10m"].append(round(wind * 3.6, 1) if wind is not None else None)

    first = series[0]
    first_dt = local(first["time"])
    inst = first["data"]["instant"]["details"]
    n1 = first["data"].get("next_1_hours") or first["data"].get("next_6_hours") or {}
    symbol = n1.get("summary", {}).get("symbol_code", "")
    if symbol.endswith("_night") or symbol.endswith("_polartwilight"):
        is_day = 0
    elif symbol.endswith("_day"):
        is_day = 1
    else:
        is_day = 1 if 6 <= first_dt.hour < 18 else 0
    temp = inst.get("air_temperature")
    rh = inst.get("relative_humidity")
    wind = inst.get("wind_speed") or 0.0
    current = {
        "time": fmt(first_dt),
        "temperature_2m": temp,
        "relative_humidity_2m": round(rh) if rh is not None else None,
        "apparent_temperature": _apparent_temperature(temp, rh, wind) if temp is not None and rh is not None else temp,
        "is_day": is_day,
        "precipitation": n1.get("details", {}).get("precipitation_amount", 0.0),
        "weather_code": _symbol_to_wmo(symbol) if symbol else 3,
        "surface_pressure": inst.get("air_pressure_at_sea_level"),
        "wind_speed_10m": round(wind * 3.6, 1),
        "wind_direction_10m": inst.get("wind_from_direction"),
    }

    dates = sorted(days)
    daily = {
        "time": dates,
        "weather_code": [max(days[d]["codes"]) if days[d]["codes"] else 3 for d in dates],
        "temperature_2m_max": [days[d]["tmax"] if days[d]["tmax"] != -math.inf else None for d in dates],
        "temperature_2m_min": [days[d]["tmin"] if days[d]["tmin"] != math.inf else None for d in dates],
        "precipitation_sum": [round(days[d]["rain"], 1) for d in dates],
        "precipitation_probability_max": [days[d]["prob"] for d in dates],
    }

    offset = first_dt.utcoffset()
    return {
        "latitude": lat,
        "longitude": lon,
        "timezone": str(tz),
        "utc_offset_seconds": int(offset.total_seconds()) if offset else 0,
        "current": current,
        "hourly": hourly,
        "daily": daily,
        "source": "met-norway",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
