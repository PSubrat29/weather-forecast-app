# Weather Forecast App

Live site: https://psubrat29.github.io/weather-forecast-app/

A weather dashboard that shows current conditions and a 7-day forecast for any city, plus a
next-hour temperature prediction from a small TensorFlow.js model trained in the browser on the
last 7 days of hourly observations.

- **Frontend**: Vue 3 + Vite, deployed to GitHub Pages. Works on its own: it calls the free,
  key-less [Open-Meteo](https://open-meteo.com/) API directly from the browser.
- **Backend (optional)**: FastAPI proxy for Open-Meteo (`/weather?latitude=..&longitude=..`).
  When `VITE_API_URL` is set at build time the frontend uses it, and falls back to Open-Meteo
  directly if the backend is down.

## Project structure
```
weather-forecast-app/
├─ .github/workflows/ci.yml   # Build + test on every push; deploy to Pages from main
├─ backend/
│  ├─ main.py                 # FastAPI app: /, /health, /weather
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ index.html
│  ├─ vite.config.js
│  ├─ package.json
│  ├─ Dockerfile
│  └─ src/
│     ├─ main.js
│     ├─ App.vue
│     ├─ components/Weather.vue
│     └─ lib/
│        ├─ api.js            # Open-Meteo / backend client, weather codes
│        └─ model.js          # TensorFlow.js next-hour temperature model
└─ docker-compose.yml
```

## Run locally

Frontend only (no backend needed):
```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173
```

With the backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# in another terminal
cd frontend
VITE_API_URL=http://localhost:8000 npm run dev
```

With Docker:
```bash
docker compose up --build
# frontend: http://localhost:8080   backend: http://localhost:8000/weather
```

## Deployment

### Frontend → GitHub Pages
1. In the repository go to **Settings → Pages → Build and deployment → Source** and choose
   **GitHub Actions** (not "Deploy from a branch" — that publishes this README instead of the app).
2. Push to `main`. The workflow builds `frontend/` and deploys `frontend/dist`.
3. Optional: to route requests through your backend, add a repository variable
   (**Settings → Secrets and variables → Actions → Variables**) named `VITE_API_URL`,
   e.g. `https://your-backend.onrender.com`.

### Backend → Render (optional)
Create a Web Service from this repo with root directory `backend`, runtime Docker
(or Python with build command `pip install -r requirements.txt` and start command
`uvicorn main:app --host 0.0.0.0 --port $PORT`).
Set `ALLOWED_ORIGINS=https://psubrat29.github.io` to restrict CORS (default `*`).

## Data
Weather data by [Open-Meteo.com](https://open-meteo.com/), licensed CC BY 4.0.
