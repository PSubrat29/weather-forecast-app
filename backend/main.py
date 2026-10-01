"""FastAPI backend that proxies the free Open-Meteo forecast API (no API key required)."""

import asyncio
import os
import time

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

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

# Open-Meteo rate-limits per IP, and hosts like Render share IPs between many apps.
# Cache responses per location so repeated page loads don't hit the upstream API.
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))
_cache: dict[tuple[float, float], tuple[float, dict]] = {}

app = FastAPI(title="Weather Forecast API")

# Comma-separated list of allowed origins; defaults to "*" so any frontend (GitHub Pages, localhost) works.
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "endpoints": ["/weather?latitude=..&longitude=..", "/health"]}


@app.get("/health")
async def health():
    # RENDER_GIT_COMMIT is set by Render; shows which commit is actually running.
    return {"status": "ok", "commit": os.getenv("RENDER_GIT_COMMIT", "local")[:7]}


@app.get("/weather")
async def weather(
    latitude: float = Query(52.52, ge=-90, le=90),
    longitude: float = Query(13.41, ge=-180, le=180),
):
    """Return the Open-Meteo forecast (current, hourly, daily) for the given coordinates."""
    key = (round(latitude, 2), round(longitude, 2))
    cached = _cache.get(key)
    if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    params = {"latitude": key[0], "longitude": key[1], **FORECAST_PARAMS}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for attempt in range(3):
                resp = await client.get(OPEN_METEO_URL, params=params)
                if resp.status_code != 429 or attempt == 2:
                    break
                await asyncio.sleep(1 + attempt)
            if resp.status_code == 429:
                if cached:
                    return cached[1]  # stale data beats no data
                raise HTTPException(status_code=503, detail="Upstream weather service is rate limiting; try again shortly")
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        if cached:
            return cached[1]
        raise HTTPException(status_code=502, detail=f"Upstream weather service error: {exc}") from exc

    _cache[key] = (time.monotonic(), data)
    if len(_cache) > 500:
        _cache.pop(next(iter(_cache)))
    return data
