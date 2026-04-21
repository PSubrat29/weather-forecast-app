from fastapi import FastAPI, HTTPException
import httpx
import asyncio

app = FastAPI()

# URLs for the selected weather data sources (using free Open-Meteo API)
DATA_SOURCES = {
    "openmeteo": "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true",
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
