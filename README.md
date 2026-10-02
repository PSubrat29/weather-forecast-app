# Weather Forecast App

Live site: https://psubrat29.github.io/weather-forecast-app/

A weather dashboard that shows current conditions and a 7-day forecast for any city, plus a
next-hour temperature prediction from a small TensorFlow.js model trained in the browser on the
last 7 days of hourly observations.

- **Frontend**: Vue 3 + Vite, deployed to GitHub Pages. Works on its own: it calls the free,
  key-less [Open-Meteo](https://open-meteo.com/) API directly from the browser.
- **Backend (optional)**: FastAPI API (`/weather?latitude=..&longitude=..`) returning data in the
  Open-Meteo format. It uses Open-Meteo first and switches to [MET Norway](https://api.met.no/)
  (also free, no key) when Open-Meteo rate-limits the server. When `VITE_API_URL` is set at build
  time the frontend uses the backend, and falls back to Open-Meteo directly if the backend is down.

## Project structure
```
weather-forecast-app/
├─ .github/workflows/ci.yml   # Build + test on every push; deploy to Pages from main
├─ backend/
│  ├─ main.py                 # FastAPI app: /, /health, /weather (Open-Meteo + MET Norway)
│  ├─ test_main.py            # pytest suite (upstream APIs mocked)
│  ├─ requirements.txt
│  └─ Dockerfile
├─ main.py, requirements.txt  # forward to backend/ for hosts that build from the repo root
├─ render.yaml                # Render Blueprint for the backend
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
Settings for the Render Web Service (also captured in `render.yaml`):

| Setting | Value |
|---|---|
| Repository / Branch | `PSubrat29/weather-forecast-app` / `main` |
| Root Directory | `backend` |
| Language | `Python 3` (3.12, pinned by `backend/.python-version`) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Environment | `ALLOWED_ORIGINS=https://psubrat29.github.io` (optional; default `*`) |

`/health` never calls external APIs. Do not use `/weather` as the health check: it depends on
third-party weather services.

Check after deploying: `<render-url>/health` returns `{"status":"ok","commit":"<deployed commit>"}`
and `<render-url>/weather` returns JSON with `"source": "open-meteo"` or `"source": "met-norway"`.

## How the backend handles rate limits
Open-Meteo limits requests per IP, and Render's free tier shares IPs between many apps, so
Open-Meteo often answers Render with HTTP 429. The backend then:
1. switches to MET Norway and converts its data to the same format;
2. stops calling Open-Meteo for the `Retry-After` period (1 hour if none is given);
3. caches each location for 10 minutes (`CACHE_TTL_SECONDS`);
4. serves stale cached data if every source fails, and only then returns 502.

The frontend waits at most 10 seconds for the backend, then calls Open-Meteo directly from the
visitor's browser, so the website keeps working even if the backend is asleep or down.

## Tests
```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

## Data
Weather data by [Open-Meteo.com](https://open-meteo.com/) and
[MET Norway](https://api.met.no/), both licensed CC BY 4.0.
