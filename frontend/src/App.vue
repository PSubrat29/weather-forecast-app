<template>
  <main class="container">
    <header>
      <h1>Weather Forecast Dashboard</h1>
      <p class="sub">Live data from Open-Meteo · next-hour temperature model trained in your browser with TensorFlow.js</p>
    </header>
    <Weather />
    <footer>Weather data by <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo.com</a> (CC BY 4.0)</footer>
  </main>
</template>

<script setup>
import Weather from './components/Weather.vue';
</script>

<style>
:root {
  --bg: #f4f7fb;
  --card: #ffffff;
  --text: #1c2430;
  --muted: #5f6b7a;
  --accent: #2563eb;
  --border: #dde3ec;
  --error: #b91c1c;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f1520;
    --card: #182130;
    --text: #e6ebf2;
    --muted: #9aa6b6;
    --accent: #60a5fa;
    --border: #2a3546;
    --error: #f87171;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
}
.container { max-width: 960px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
h1 { margin: 0 0 0.25rem; font-size: 1.75rem; }
.sub { margin: 0 0 1.5rem; color: var(--muted); }
footer { margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }
a { color: var(--accent); }
</style>
