// Weather data access. Uses the FastAPI backend when VITE_API_URL is set,
// otherwise calls the free, CORS-enabled Open-Meteo API directly from the browser.

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const FORECAST_URL = 'https://api.open-meteo.com/v1/forecast';
const GEOCODE_URL = 'https://geocoding-api.open-meteo.com/v1/search';

export const FORECAST_PARAMS = {
  current: 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m',
  hourly: 'temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m',
  daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max',
  past_days: '7',
  forecast_days: '7',
  timezone: 'auto'
};

async function getJson(url, timeoutMs = 15000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const resp = await fetch(url, { signal: ctrl.signal });
    if (!resp.ok) throw new Error(`Request failed (${resp.status})`);
    return await resp.json();
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('Request timed out');
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

function qs(params) {
  return new URLSearchParams(params).toString();
}

export async function fetchForecast(latitude, longitude) {
  const coords = { latitude: String(latitude), longitude: String(longitude) };
  if (API_BASE) {
    try {
      // Free hosting tiers sleep when idle; don't make users wait for a cold start.
      const data = await getJson(`${API_BASE}/weather?${qs(coords)}`, 10000);
      if (data && data.current && data.hourly && data.daily) return data;
      throw new Error('unexpected response format');
    } catch (e) {
      console.warn('Backend unavailable, falling back to Open-Meteo directly:', e.message);
    }
  }
  return getJson(`${FORECAST_URL}?${qs({ ...coords, ...FORECAST_PARAMS })}`);
}

export async function searchCities(name) {
  const data = await getJson(`${GEOCODE_URL}?${qs({ name, count: '6', language: 'en', format: 'json' })}`);
  return data.results || [];
}

// WMO weather interpretation codes -> label + icon
const WMO = {
  0: ['Clear sky', '☀️'], 1: ['Mainly clear', '🌤️'], 2: ['Partly cloudy', '⛅'], 3: ['Overcast', '☁️'],
  45: ['Fog', '🌫️'], 48: ['Rime fog', '🌫️'],
  51: ['Light drizzle', '🌦️'], 53: ['Drizzle', '🌦️'], 55: ['Dense drizzle', '🌧️'],
  56: ['Freezing drizzle', '🌧️'], 57: ['Freezing drizzle', '🌧️'],
  61: ['Light rain', '🌦️'], 63: ['Rain', '🌧️'], 65: ['Heavy rain', '🌧️'],
  66: ['Freezing rain', '🌧️'], 67: ['Freezing rain', '🌧️'],
  71: ['Light snow', '🌨️'], 73: ['Snow', '🌨️'], 75: ['Heavy snow', '❄️'], 77: ['Snow grains', '🌨️'],
  80: ['Rain showers', '🌦️'], 81: ['Rain showers', '🌧️'], 82: ['Violent showers', '⛈️'],
  85: ['Snow showers', '🌨️'], 86: ['Snow showers', '❄️'],
  95: ['Thunderstorm', '⛈️'], 96: ['Thunderstorm, hail', '⛈️'], 99: ['Thunderstorm, hail', '⛈️']
};

export function describeCode(code) {
  const [label, icon] = WMO[code] || ['Unknown', '❔'];
  return { label, icon };
}
