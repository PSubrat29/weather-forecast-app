# Weather Forecast App

This repository contains a prototype weather‑forecast dashboard built with:
- **Backend**: FastAPI (Python) – aggregates data from NASA, IMD, JAXA, and NOAA (placeholder endpoints).
- **Frontend**: Vue 3 + Vite – UI to display the combined JSON and run a TensorFlow.js model in the browser.
- **AI/ML**: TensorFlow.js model is loaded from a URL (replace with your model). Currently a placeholder is used.

## Project structure
```
weather-forecast-app/
├─ backend/
│  └─ main.py          # FastAPI server exposing /weather
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.js
│  ├─ public/index.html
│  └─ src/
│     ├─ main.js
│     ├─ App.vue
│     └─ components/Weather.vue
└─ README.md
```

## Setup
1. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # on Windows use .venv\Scripts\activate
   pip install fastapi uvicorn httpx
   uvicorn main:app --reload --port 8000
   ```
2. **Frontend**
   ```bash
   cd ../frontend
   npm install
   npm run dev   # Vite dev server runs on http://localhost:5173
   ```
   The dev server proxies `/weather` calls to the FastAPI backend.

## Next steps
- The backend currently uses the free Open-Meteo API (no key required). You can change the latitude/longitude or add more sources in `backend/main.py`.
- Host a trained TensorFlow.js model and update the URL in `Weather.vue` (`tf.loadLayersModel`).
- Extend the UI to visualise predictions.

The code is ready for further development and customization.
