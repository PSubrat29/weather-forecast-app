<template>
  <div>
    <button @click="loadData" :disabled="loading">Load Weather Data</button>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-else-if="weatherData">
      <pre>{{ weatherData }}</pre>
      <div v-if="prediction">Model prediction: {{ prediction }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import * as tf from '@tensorflow/tfjs';

const loading = ref(false);
const error = ref(null);
const weatherData = ref(null);
const prediction = ref(null);

// Placeholder model loading – replace URL with actual model.json when ready
let model = null;
async function loadModel() {
  if (!model) {
    try {
      model = await tf.loadLayersModel('https://example.com/path/to/model.json');
    } catch (e) {
      console.warn('Failed to load model, using dummy prediction');
    }
  }
}

async function loadData() {
  loading.value = true;
  error.value = null;
  weatherData.value = null;
  prediction.value = null;
  try {
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const endpoint = baseUrl ? `${baseUrl}/weather` : '/weather';
    const resp = await axios.get(endpoint);
    weatherData.value = resp.data;
    await loadModel();
    // Dummy preprocessing – flatten JSON values into a tensor
    const flat = Object.values(resp.data)
      .map(v => typeof v === 'object' ? JSON.stringify(v) : v)
      .join(' ');
    const inputTensor = tf.tensor([flat.length]); // placeholder scalar tensor
    if (model) {
      const pred = model.predict(inputTensor);
      prediction.value = pred.arraySync();
    } else {
      prediction.value = 'No model loaded – placeholder result';
    }
  } catch (e) {
    error.value = e.message || 'Failed to fetch weather data';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
button { margin-bottom: 1rem; }
.error { color: red; }
pre { background: #f0f0f0; padding: 1rem; }
</style>
