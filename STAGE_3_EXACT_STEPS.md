# STAGE 3: EXACT GITHUB PAGES FRONTEND DEPLOYMENT STEPS
## Your backend is LIVE at: https://weather-forecast-backend-iknr.onrender.com/weather
## Now deploy the frontend to GitHub Pages

You have successfully verified your backend returns weather data at:
`https://weather-forecast-backend-iknr.onrender.com/weather`

Now let's deploy the frontend to GitHub Pages so it can talk to your live backend.

---

## 📋 PRE-FLIGHT CHECK - VERIFY THESE FIRST
Before starting, confirm in your project:
1. [ ] `frontend/src/components/Weather.vue` exists
2. [ ] `frontend/public/model/model.json` exists
3. [ ] `frontend/public/model/group1-shard1of1` exists
4. [ ] `frontend/vite.config.js` is present
5. [ ] Your GitHub repo is at: `https://github.com/PSubrat29/weather-forecast-app`

---

## 🚀 STEP-BY-STEP GITHUB PAGES DEPLOYMENT WITH BACKEND CONFIG

### 🔹 STEP 1: CREATE PRODUCTION ENVIRONMENT FILE
This tells the frontend where to find your backend in production.

In your project folder, run:
```bash
cd /d D:\ParidaUser\Claude-Project\weather-forecast-app\frontend
echo VITE_API_URL=https://weather-forecast-backend-iknr.onrender.com > .env.production
```

**Verify the file was created correctly:**
```bash
type .env.production
```
Should show: `VITE_API_URL=https://weather-forecast-backend-iknr.onrender.com`

### 🔹 STEP 2: INSTALL GH-PAGES (ONE-TIME SETUP)
```bash
"C:\Program Files\nodejs\npm.cmd" install --save-dev gh-pages
```
Wait for installation to complete (you'll see added packages).

### 🔹 STEP 3: ADD DEPLOY SCRIPT TO PACKAGE.JSON
1. Open `frontend/package.json` in a text editor (Notepad, VS Code, etc.)
2. Find the `"scripts"` section (should be near the top, around line 5)
3. Add this line inside the scripts object:
   ```json
   "deploy": "gh-pages -d dist"
   ```
4. The scripts section should now look like:
   ```json
   "scripts": {
     "dev": "vite",
     "build": "vite build",
     "preview": "vite preview",
     "deploy": "gh-pages -d dist"
   }
   ```
5. **Save the file**

### 🔹 STEP 4: BUILD FRONTEND FOR PRODUCTION
```bash
"C:\Program Files\nodejs\npm.cmd" run build
```
This will:
- Process your Vue.js code
- Optimize and minify assets
- Create a `dist/` folder with production-ready files
- Take 10-30 seconds to complete

### 🔹 STEP 5: DEPLOY TO GITHUB PAGES
```bash
"C:\Program Files\nodejs\npm.cmd" run deploy
```
This will:
- Build the frontend (if not already built)
- Push the contents of the `dist/` folder to a `gh-pages` branch
- Automatically configure GitHub Pages
- Take 1-2 minutes to complete

You'll see output like:
```
> weather-forecast-frontend@0.1.0 deploy
> gh-pages -d dist

Published : https://PSubrat29.github.io/weather-forecast-app/
```

### 🔹 STEP 6: VERIFY GITHUB PAGES IS CONFIGURED
1. Go to your GitHub repo: `https://github.com/PSubrat29/weather-forecast-app`
2. Click **Settings** (top right) → **Pages** (left sidebar)
3. Under "Source":
   - **Branch**: `gh-pages` (should be selected)
   - **Folder**: `/ (root)` (should be selected)
4. If not set correctly, select these options and click **Save**
5. GitHub will show your live site URL at the top of the Pages section

### 🔹 STEP 7: ACCESS YOUR LIVE APP
Visit: `https://PSubrat29.github.io/weather-forecast-app/`

📝 **Important**: The first load might take 10-15 seconds as GitHub Pages serves the static files from the `gh-pages` branch.

---

## 🔍 HOW THE API CONFIGURATION WORKS
In `frontend/src/components/Weather.vue`:
```javascript
const baseUrl = import.meta.env.VITE_API_URL || '';
const endpoint = baseUrl ? `${baseUrl}/weather` : '/weather';
```

- **With `.env.production`** (what we just created): 
  - `VITE_API_URL` is set to `https://weather-forecast-backend-iknr.onrender.com`
  - `endpoint` becomes: `https://weather-forecast-backend-iknr.onrender.com/weather`
  - Frontend calls your **live Render backend**

- **In development** (`npm run dev` without .env.production):
  - `VITE_API_URL` is empty
  - `endpoint` becomes: `/weather`
  - Vite's proxy (in `vite.config.js`) forwards `/weather` to `http://localhost:8000/weather`
  - Frontend calls your **local development backend**

---

## ✅ VERIFICATION CHECKLIST FOR YOUR LIVE APP
After deployment, verify:
- [ ] Visit: `https://PSubrat29.github.io/weather-forecast-app/`
- [ ] You see: "Weather Forecast Dashboard" heading
- [ ] Click the **"Load Weather Data"** button
- [ ] Button shows "Loading..." briefly, then shows data
- [ ] You see JSON weather data in the output (from your Render backend)
- [ ] You see a line: "Model prediction: [some number]"
- [ ] No red error messages in the output or browser console
- [ ] Button works repeatedly (not permanently stuck on "Loading")

### Expected Output After Clicking Button:
You should see something like:
```
{
  "openmeteo": {
    "latitude": 52.52,
    "longitude": 13.419998,
    "generationtime_ms": 0.066,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 38,
    "current_weather_units": { ... },
    "current_weather": {
      "time": "2026-04-22T17:00",
      "interval": 900,
      "temperature": 16.5,
      "windspeed": 15.4,
      "winddirection": 327,
      "is_day": 1,
      "weathercode": 0
    }
  }
}
Model prediction: 0
```
(The prediction shows "0" because we used a demo model with zero weights - this is expected!)

---

## 🛠️ TROUBLESHOOTING COMMON ISSUES

**Issue**: Button shows "Failed to fetch weather data" or network error
- **Fix**:
  1. Press F12 → Console tab in browser
  2. Look for the exact error message
  3. Check what URL it's trying to fetch
  4. Should be: `https://weather-forecast-backend-iknr.onrender.com/weather`
  5. If it's trying to fetch from github.io (e.g., `https://PSubrat29.github.io/weather-forecast-app/weather`):
     - `.env.production` file missing or incorrect
     - Re-run: `echo VITE_API_URL=https://weather-forecast-backend-iknr.onrender.com > .env.production`
     - Rebuild: `npm run build`
     - Redeploy: `npm run deploy`

**Issue**: Blank page or "Cannot GET /"
- **Fix**:
  1. Verify GitHub Pages is set to `gh-pages` branch in Settings → Pages
  2. Wait 1-2 minutes after enabling Pages for DNS propagation
  3. Clear browser cache (Ctrl+Shift+R) or try incognito mode
  4. Check that the `dist/` folder was actually deployed to the `gh-pages` branch

**Issue**: Model fails to load (errors in console about 404 on model files)
- **Fix**:
  1. Verify files exist in `frontend/public/model/` on GitHub
  2. Check that they were included in the build (look in `gh-pages` branch on GitHub)
  3. If missing, ensure `.gitignore` doesn't accidentally exclude them
  4. Rebuild and redeploy

**Issue**: Button stays stuck on "Loading..." for more than 20 seconds
- **Fix**:
  1. Your Render backend may be sleeping (free tier sleeps after 15 min of inactivity)
  2. Wait 10-20 seconds for it to spin up
  3. Try clicking the button again
  4. Subsequent requests will be fast (< 2 seconds)

**Issue**: You see CORS error in console
- **Fix**: This should not happen with our setup. If it does:
  1. Check that you're calling the exact Render URL
  2. Verify no trailing slashes or extra characters in `.env.production`
  3. Redeploy frontend after fixing `.env.production`

---

## 🎯 YOU'RE DONE!
Your full stack is now live and working:
- **Frontend**: `https://PSubrat29.github.io/weather-forecast-app/`
- **Backend**: `https://weather-forecast-backend-iknr.onrender.com/weather`

The app will:
1. Fetch real-time weather data from Open-Meteo API via your Render backend
2. Run it through your TensorFlow.js model (demo version with zero weights)
3. Display both the raw weather data and the model prediction
4. Work for anyone, anywhere in the world - completely free and secure

---

## 🔄 UPDATING YOUR APPLICATION
To make changes later:
1. **Frontend changes** (UI, model, etc.):
   - Edit files in `frontend/`
   - `"C:\Program Files\nodejs\npm.cmd" run build`
   - `"C:\Program Files\nodejs\npm.cmd" run deploy`
2. **Backend changes** (API logic, etc.):
   - Edit files in `backend/`
   - `git add . && git commit -m "Your message"`
   - `git push origin main`
   - Render automatically detects the push and redeploys (watch logs in Render dashboard)
3. **Model updates** (when you have a real trained model):
   - Replace files in `frontend/public/model/`
   - Rebuild and redeploy frontend: `npm run build` then `npm run deploy`

**Ready to test?** Follow the steps above to create `.env.production`, install gh-pages, build, deploy, then visit your live app. Let me know when you see weather data and a prediction!