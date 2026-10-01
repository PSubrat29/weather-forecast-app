import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // Relative base so the build works at any sub-path (e.g. GitHub Pages /weather-forecast-app/).
  base: './',
  build: {
    chunkSizeWarningLimit: 2000
  }
});
