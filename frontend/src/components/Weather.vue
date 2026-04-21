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

// Load our locally hosted model
let model = null;
async function loadModel() {
  if (!model) {
    try {
      // Load model from our public directory
      model = await tf.loadLayersModel('/model/model.json');
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
    // Extract numerical features from weather data for model input
    const features = extractFeatures(resp.data);
    const inputTensor = tf.tensor2d([features]); // [1, num_features] tensor
    if (model) {
      const pred = model.predict(inputTensor);
      prediction.value = Array.isArray(pred.arraySync()) ? pred.arraySync()[0] : pred.arraySync();
    } else {
      prediction.value = 'No model loaded – placeholder result';
    }
  } catch (e) {
    error.value = e.message || 'Failed to fetch weather data';
  } finally {
    loading.value = false;
  }
}

// Extract numerical features from weather data for model input
function extractFeatures(data) {
  // For Open-Meteo API response, extract key numerical values
  const features = [];

  // Handle Open-Meteo response structure
  if (data.openmeteo && data.openmeteo.current_weather) {
    const weather = data.openmeteo.current_weather;
    features.push(weather.temperature || 0);           // temperature
    features.push(weather.windspeed || 0);             // windspeed
    features.push(weather.winddirection || 0);         // winddirection
    features.push(weather.is_day || 0);                // is_day
    features.push(weather.weathercode || 0);           // weathercode
  } else {
    // Fallback: extract any numerical values we can find
    function extractNumerical(obj, arr) {
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          const value = obj[key];
          if (typeof value === 'number' && !isNaN(value)) {
            arr.push(value);
          } else if (typeof value === 'object' && value !== null) {
            extractNumerical(value, arr);
          }
        }
      }
    }
    extractNumerical(data, features);

    // Ensure we have at least 4 features for our model
    while (features.length < 4) {
      features.push(0);
    }
    // Limit to first 4 features to match model input shape
    features.splice(4);
  }

  return features;
}
</script>

<style scoped>
button { margin-bottom: 1rem; }
.error { color: red; }
pre { background: #f0f0f0; padding: 1rem; }
</style>
