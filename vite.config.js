import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // Development proxy for local FastAPI server
  server: {
    proxy: process.env.NODE_ENV === 'development' ? {
      '/weather': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    } : undefined
  },
  // Public base URL for production (set via VITE_API_URL in .env.production)
  define: {
    __API_BASE__: JSON.stringify(process.env.VITE_API_URL || '')
  }
});
