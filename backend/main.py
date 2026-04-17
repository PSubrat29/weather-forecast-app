from fastapi import FastAPI, HTTPException
import httpx
import asyncio

app = FastAPI()

# URLs for the selected weather data sources (placeholder endpoints)
DATA_SOURCES = {
    "nasa": "https://api.nasa.gov/planetary/weather",  # replace with real NASA endpoint & key
    "imd": "https://api.imd.gov.in/v1/weather",       # replace with real IMD endpoint & key
    "jaxa": "https://api.jaxa.jp/v1/weather",       # replace with real JAXA endpoint & key
    "noaa": "https://www.noaa.gov/api/weather"      # replace with real NOAA endpoint & key
}

async def fetch(source_url: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(source_url)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch {source_url}: {exc}")

@app.get("/weather")
async def combined_weather():
    """Fetch weather data from all configured sources and return a merged JSON."""
    tasks = [fetch(url) for url in DATA_SOURCES.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    merged = {}
    for name, result in zip(DATA_SOURCES.keys(), results):
        if isinstance(result, Exception):
            merged[name] = {"error": str(result)}
        else:
            merged[name] = result
    return merged
