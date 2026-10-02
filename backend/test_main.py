"""Backend tests. Upstream APIs are mocked; run with `pytest` from the backend directory."""

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

import main


def met_fixture(start: datetime) -> dict:
    """MET Norway Locationforecast 'complete' response: 60 hourly steps, then 6-hourly."""
    series = []
    t = start
    for i in range(60):
        series.append({
            "time": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "instant": {"details": {
                    "air_pressure_at_sea_level": 1012.0 + i % 3,
                    "air_temperature": 10.0 + (i % 24) / 2,
                    "relative_humidity": 70.0,
                    "wind_from_direction": 225.0,
                    "wind_speed": 5.0,
                }},
                "next_1_hours": {
                    "summary": {"symbol_code": "rainshowers_day" if i % 24 == 12 else "partlycloudy_night"},
                    "details": {"precipitation_amount": 0.5, "probability_of_precipitation": 40.0},
                },
                "next_6_hours": {
                    "summary": {"symbol_code": "cloudy"},
                    "details": {"air_temperature_max": 16.0, "air_temperature_min": 9.0,
                                "precipitation_amount": 1.0, "probability_of_precipitation": 30.0},
                },
            },
        })
        t += timedelta(hours=1)
    t = t.replace(hour=(t.hour // 6 + 1) * 6 % 24) + (timedelta(days=1) if t.hour >= 18 else timedelta())
    for _ in range(28):
        series.append({
            "time": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "instant": {"details": {"air_pressure_at_sea_level": 1010.0, "air_temperature": 12.0,
                                        "relative_humidity": 65.0, "wind_from_direction": 180.0, "wind_speed": 3.0}},
                "next_6_hours": {
                    "summary": {"symbol_code": "lightrainandthunder"},
                    "details": {"air_temperature_max": 18.0, "air_temperature_min": 8.0,
                                "precipitation_amount": 2.0, "probability_of_precipitation": 60.0},
                },
            },
        })
        t += timedelta(hours=6)
    return {"type": "Feature", "properties": {"meta": {}, "timeseries": series}}


OPEN_METEO_BODY = {"latitude": 52.52, "current": {"time": "2026-10-01T12:00"}, "hourly": {}, "daily": {}}


@pytest.fixture
def upstream(monkeypatch):
    """Route upstream calls to programmable fake responses and record them."""
    state = {"open_meteo": 200, "met": 200, "calls": []}
    start = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)

    async def fake_get(self, url, params=None):
        name = "met" if "met.no" in url else "open_meteo"
        state["calls"].append(name)
        assert self.headers["user-agent"].startswith("weather-forecast-app/")
        status = state[name]
        body = met_fixture(start) if name == "met" else dict(OPEN_METEO_BODY)
        return httpx.Response(status, json=body if status == 200 else {"error": True},
                              request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    monkeypatch.setattr(main, "_open_meteo_blocked_until", 0.0)
    main._cache.clear()
    return state


@pytest.fixture
def client():
    return TestClient(main.app)


def test_health_and_root_support_get_and_head(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.head("/health").status_code == 200
    assert client.get("/").status_code == 200
    assert client.head("/").status_code == 200


def test_rejects_invalid_coordinates(client):
    assert client.get("/weather?latitude=100&longitude=0").status_code == 422


def test_uses_open_meteo_when_available(client, upstream):
    r = client.get("/weather")
    assert r.status_code == 200
    assert r.json()["source"] == "open-meteo"
    assert upstream["calls"] == ["open_meteo"]


def test_falls_back_to_met_norway_on_429_and_stops_calling_open_meteo(client, upstream):
    upstream["open_meteo"] = 429
    r = client.get("/weather?latitude=19.07&longitude=72.88")
    assert r.status_code == 200
    assert r.json()["source"] == "met-norway"
    assert upstream["calls"] == ["open_meteo", "met"]

    upstream["calls"].clear()
    r = client.get("/weather?latitude=40.7&longitude=-74.0")  # different location, not cached
    assert r.status_code == 200
    assert upstream["calls"] == ["met"]  # Open-Meteo skipped during cooldown


def test_caches_per_location(client, upstream):
    client.get("/weather?latitude=10&longitude=20")
    client.get("/weather?latitude=10.001&longitude=20")
    assert upstream["calls"] == ["open_meteo"]


def test_returns_502_when_all_sources_fail(client, upstream):
    upstream["open_meteo"] = 500
    upstream["met"] = 503
    r = client.get("/weather")
    assert r.status_code == 502
    assert "All weather sources failed" in r.json()["detail"]


def test_serves_stale_cache_when_all_sources_fail(client, upstream):
    client.get("/weather")
    key = next(iter(main._cache))
    ts, data = main._cache[key]
    main._cache[key] = (ts - 10_000, data)
    upstream["open_meteo"] = 500
    upstream["met"] = 500
    r = client.get("/weather")
    assert r.status_code == 200
    assert r.headers["x-data-stale"] == "true"


def test_met_conversion_matches_open_meteo_format():
    data = main.met_to_open_meteo(met_fixture(datetime(2026, 10, 1, 10, tzinfo=timezone.utc)), 19.07, 72.88)
    assert data["timezone"] == "Asia/Kolkata"
    assert data["utc_offset_seconds"] == 19800
    cur = data["current"]
    assert cur["time"] == "2026-10-01T15:30"  # 10:00 UTC in IST
    assert set(cur) >= set(main.FORECAST_PARAMS["current"].split(","))
    assert cur["wind_speed_10m"] == 18.0  # 5 m/s -> km/h
    assert cur["is_day"] == 0  # partlycloudy_night
    assert cur["weather_code"] == 2

    hourly = data["hourly"]
    assert len(hourly["time"]) == 60
    assert all(len(v) == 60 for v in hourly.values())
    for k in main.FORECAST_PARAMS["hourly"].split(","):
        assert k in hourly

    daily = data["daily"]
    assert len(daily["time"]) >= 7
    for k in main.FORECAST_PARAMS["daily"].split(","):
        assert len(daily[k]) == len(daily["time"])
    assert all(mx >= mn for mx, mn in zip(daily["temperature_2m_max"], daily["temperature_2m_min"]))
    assert daily["weather_code"][-1] == 95  # thunder in the 6-hourly tail
    assert daily["precipitation_probability_max"][0] == 40.0


@pytest.mark.parametrize("symbol,code", [
    ("clearsky_day", 0), ("fair_night", 1), ("cloudy", 3), ("fog", 45), ("heavyrain", 65),
    ("lightssnowshowersandthunder_day", 95), ("heavysnowshowers_polartwilight", 86), ("unknownthing", 3),
])
def test_symbol_mapping(symbol, code):
    assert main._symbol_to_wmo(symbol) == code
