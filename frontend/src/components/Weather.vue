<template>
  <section>
    <form class="search" @submit.prevent="onSearch">
      <input v-model="query" type="search" placeholder="Search a city (e.g. London, Mumbai)" aria-label="City" />
      <button type="submit" :disabled="loading || !query.trim()">Search</button>
      <button type="button" class="secondary" :disabled="loading" @click="useMyLocation">Use my location</button>
    </form>

    <ul v-if="results.length" class="results">
      <li v-for="r in results" :key="r.id">
        <button type="button" class="link" @click="selectPlace(r)">
          {{ r.name }}<span v-if="r.admin1">, {{ r.admin1 }}</span><span v-if="r.country">, {{ r.country }}</span>
        </button>
      </li>
    </ul>

    <div v-if="error" class="error" role="alert">{{ error }}</div>
    <div v-if="loading" class="muted">Loading weather…</div>

    <template v-if="data && !loading">
      <div class="card current">
        <div>
          <h2>{{ place.label }}</h2>
          <div class="muted">Updated {{ formatTime(data.current.time) }} (local time) · Source: <a :href="sourceInfo.url" target="_blank" rel="noopener">{{ sourceInfo.name }}</a></div>
        </div>
        <div class="now">
          <span class="icon">{{ currentDesc.icon }}</span>
          <span class="temp">{{ round(data.current.temperature_2m) }}°C</span>
        </div>
        <div class="muted">{{ currentDesc.label }} · feels like {{ round(data.current.apparent_temperature) }}°C</div>
        <dl class="grid">
          <div><dt>Humidity</dt><dd>{{ data.current.relative_humidity_2m }}%</dd></div>
          <div><dt>Wind</dt><dd>{{ round(data.current.wind_speed_10m) }} km/h {{ compass(data.current.wind_direction_10m) }}</dd></div>
          <div><dt>Pressure</dt><dd>{{ round(data.current.surface_pressure) }} hPa</dd></div>
          <div><dt>Precipitation</dt><dd>{{ data.current.precipitation }} mm</dd></div>
        </dl>
      </div>

      <div class="card">
        <h3>Next-hour temperature</h3>
        <div v-if="modelState === 'training'" class="muted">Training model on hourly data…</div>
        <div v-else-if="modelState === 'error'" class="error">{{ modelError }}</div>
        <dl v-else-if="prediction" class="grid">
          <div><dt>TensorFlow.js model</dt><dd>{{ prediction.temperature.toFixed(1) }}°C</dd></div>
          <div><dt>{{ sourceInfo.name }} forecast</dt><dd>{{ nextHourForecast !== null ? nextHourForecast.toFixed(1) + '°C' : '—' }}</dd></div>
          <div><dt>Training error (RMSE)</dt><dd>±{{ prediction.rmse.toFixed(2) }}°C</dd></div>
          <div><dt>Training data</dt><dd>{{ prediction.samples }} hours ({{ prediction.basis }})</dd></div>
        </dl>
      </div>

      <div class="card">
        <h3>7-day forecast</h3>
        <div class="days">
          <div v-for="d in days" :key="d.date" class="day">
            <div class="dname">{{ d.name }}</div>
            <div class="icon" :title="d.desc.label">{{ d.desc.icon }}</div>
            <div><strong>{{ round(d.max) }}°</strong> <span class="muted">{{ round(d.min) }}°</span></div>
            <div class="muted small">{{ d.rain }} mm<span v-if="d.prob !== null"> · {{ d.prob }}%</span></div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { fetchForecast, searchCities, describeCode } from '../lib/api.js';
import { predictNextHour } from '../lib/model.js';

const DEFAULT_PLACE = { label: 'Berlin, Germany', latitude: 52.52, longitude: 13.41 };

const query = ref('');
const results = ref([]);
const loading = ref(false);
const error = ref(null);
const data = ref(null);
const place = ref(DEFAULT_PLACE);
const prediction = ref(null);
const modelState = ref('idle');
const modelError = ref('');
let requestId = 0;

const round = (v) => (typeof v === 'number' ? Math.round(v) : '—');
const formatTime = (t) => t.replace('T', ' ');
const compass = (deg) => ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.round(deg / 45) % 8];

const sourceInfo = computed(() =>
  data.value.source === 'met-norway'
    ? { name: 'MET Norway', url: 'https://api.met.no/' }
    : { name: 'Open-Meteo', url: 'https://open-meteo.com/' }
);
const currentDesc = computed(() => describeCode(data.value.current.weather_code));

const days = computed(() => {
  const d = data.value.daily;
  const today = data.value.current.time.slice(0, 10);
  return d.time
    .map((date, i) => ({
      date,
      name: date === today ? 'Today' : new Date(date + 'T12:00').toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' }),
      desc: describeCode(d.weather_code[i]),
      max: d.temperature_2m_max[i],
      min: d.temperature_2m_min[i],
      rain: d.precipitation_sum[i] ?? 0,
      prob: d.precipitation_probability_max?.[i] ?? null
    }))
    .filter((x) => x.date >= today)
    .slice(0, 7);
});

const nextHourForecast = computed(() => {
  const h = data.value.hourly;
  const now = Date.parse(data.value.current.time);
  const i = h.time.findIndex((t) => Date.parse(t) > now);
  return i >= 0 && typeof h.temperature_2m[i] === 'number' ? h.temperature_2m[i] : null;
});

async function load(p) {
  const id = ++requestId;
  loading.value = true;
  error.value = null;
  prediction.value = null;
  modelState.value = 'idle';
  try {
    const result = await fetchForecast(p.latitude, p.longitude);
    if (id !== requestId) return;
    if (!result || !result.current || !result.daily || !result.hourly) {
      throw new Error(result?.reason || 'Unexpected response from weather service');
    }
    data.value = result;
    place.value = p;
  } catch (e) {
    if (id === requestId) error.value = `Could not load weather: ${e.message}`;
    return;
  } finally {
    if (id === requestId) loading.value = false;
  }
  runModel(id);
}

async function runModel(id) {
  modelState.value = 'training';
  try {
    const p = await predictNextHour(data.value);
    if (id !== requestId) return;
    prediction.value = p;
    modelState.value = 'done';
  } catch (e) {
    if (id !== requestId) return;
    modelError.value = `Model unavailable: ${e.message}`;
    modelState.value = 'error';
  }
}

async function onSearch() {
  const q = query.value.trim();
  if (!q) return;
  error.value = null;
  try {
    results.value = await searchCities(q);
    if (!results.value.length) error.value = `No places found for "${q}"`;
  } catch (e) {
    error.value = `City search failed: ${e.message}`;
  }
}

function selectPlace(r) {
  results.value = [];
  query.value = '';
  const label = [r.name, r.country].filter(Boolean).join(', ');
  load({ label, latitude: r.latitude, longitude: r.longitude });
}

function useMyLocation() {
  if (!navigator.geolocation) {
    error.value = 'Geolocation is not supported by this browser';
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => load({
      label: 'My location',
      latitude: +pos.coords.latitude.toFixed(4),
      longitude: +pos.coords.longitude.toFixed(4)
    }),
    (err) => { error.value = `Location unavailable: ${err.message}`; },
    { timeout: 10000 }
  );
}

onMounted(() => load(DEFAULT_PLACE));
</script>

<style scoped>
.search { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
input {
  flex: 1 1 220px; padding: 0.6rem 0.8rem; font-size: 1rem;
  border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--text);
}
button {
  padding: 0.6rem 1rem; font-size: 1rem; border: 0; border-radius: 8px;
  background: var(--accent); color: #fff; cursor: pointer;
}
button.secondary { background: transparent; color: var(--accent); border: 1px solid var(--accent); }
button:disabled { opacity: 0.5; cursor: default; }
button.link { background: none; color: var(--accent); padding: 0.25rem 0; text-align: left; }
.results { list-style: none; margin: 0 0 1rem; padding: 0.5rem 1rem; background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
h2 { margin: 0; font-size: 1.35rem; }
h3 { margin: 0 0 0.75rem; font-size: 1.1rem; }
.muted { color: var(--muted); }
.small { font-size: 0.85rem; }
.error { color: var(--error); margin: 0.5rem 0 1rem; }
.now { display: flex; align-items: center; gap: 0.5rem; margin: 0.75rem 0 0.25rem; }
.now .icon { font-size: 2.5rem; }
.temp { font-size: 2.75rem; font-weight: 600; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin: 1rem 0 0; }
.grid dt { color: var(--muted); font-size: 0.85rem; }
.grid dd { margin: 0.15rem 0 0; font-size: 1.1rem; font-weight: 600; }
.days { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 0.5rem; }
.day { text-align: center; padding: 0.5rem; border: 1px solid var(--border); border-radius: 8px; }
.day .icon { font-size: 1.75rem; margin: 0.25rem 0; }
.dname { font-weight: 600; }
</style>
