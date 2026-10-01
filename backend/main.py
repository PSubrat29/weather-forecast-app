"""FastAPI backend that proxies the free Open-Meteo forecast API (no API key required)."""

import os

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
    return {"status": "ok"}


@app.get("/weather")
async def weather(
    latitude: float = Query(52.52, ge=-90, le=90),
    longitude: float = Query(13.41, ge=-180, le=180),
):
    """Return the Open-Meteo forecast (current, hourly, daily) for the given coordinates."""
    params = {"latitude": latitude, "longitude": longitude, **FORECAST_PARAMS}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream weather service error: {exc}") from exc
