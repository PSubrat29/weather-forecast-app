# STAGE 3: GITHUB PAGES FRONTEND DEPLOYMENT
## Exact Step-by-Step Instructions

Your backend is now live at: `https://weather-forecast-backend-iknr.onrender.com`

Now let's deploy the frontend to GitHub Pages.

---

## 📋 PRE-FLIGHT CHECK (Verify before starting)
Make sure these are correct in your GitHub repo:
- [ ] `frontend/src/components/Weather.vue` loads model from `/model/model.json`
- [ ] `frontend/public/model/model.json` and `frontend/public/model/group1-shard1of1` exist
- [ ] `frontend/vite.config.js` has proxy setup for development (will be ignored in production)
- [ ] No `.env` file needed for frontend (model is public)

---

## 🚀 STEP-BY-STEP GITHUB PAGES DEPLOYMENT

We'll use the `gh-pages` npm package for easy deployment.

### Step 1: Install gh-pages (One-time Setup)
Open Git Bash or Command Prompt in your project folder:
```bash
cd /d D:\ParidaUser\Claude-Project\weather-forecast-app\frontend
"C:\Program Files\nodejs\npm.cmd" install --save-dev gh-pais
```
Wait for installation to complete.

### Step 2: Add Deploy Script to package.json
1. Open `frontend/package.json` in a text editor (Notepad, VS Code, etc.)
2. Find the `"scripts"` section (should be near the top)
3. Add this line inside the scripts object:
   ```json
   "deploy": "gh-pages -d dist"
   ```
4. It should look like:
   ```json
   "scripts": {
     "dev": "vite",
     "build": "vite build",
     "preview": "vite preview",
     "deploy": "gh-pages -d dist"
   }
   ```
5. Save the file.

### Step 3: Build the Frontend for Production
```bash
"C:\Program Files\nodejs\npm.cmd" run build
```
This creates a `dist/` folder with production-ready files.

### Step 4: Deploy to GitHub Pages
```bash
"C:\Program Files\nodejs\npm.cmd" run deploy
```
This will:
- Build the frontend (if not already built)
- Push the contents of `dist/` to a `gh-pages` branch
- Automatically configure GitHub Pages

### Step 5: Verify GitHub Pages is Enabled
1. Go to your GitHub repo: `https://github.com/PSubrat29/weather-forecast-app`
2. Click **Settings** → **Pages** (left sidebar)
3. Under "Source":
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. If not set, select these options and click **Save**
5. GitHub will show your live site URL (usually appears within 1-2 minutes)

### Step 6: Access Your Live App
Visit: `https://PSubrat29.github.io/weather-forecast-app/`

📝 **Note**: The first load might take 10-15 seconds as GitHub Pages serves the static files.

---

## 🔧 IMPORTANT CONFIGURATION FOR PRODUCTION

Your frontend is already configured to work with GitHub Pages + Render.com backend:

### How API Calls Work:
In `frontend/src/components/Weather.vue`:
```javascript
const baseUrl = import.meta.env.VITE_API_URL || '';
const endpoint = baseUrl ? `${baseUrl}/weather` : '/weather';
```
- **In development** (`npm run dev`): `VITE_API_URL` is empty → uses `/weather` → Vite proxy forwards to `http://localhost:8000/weather`
- **In production** (GitHub Pages): `VITE_API_URL` is empty → uses `/weather` → **relative to your GitHub Pages domain**

### Wait - That Won't Work with Render.com!
Actually, we need to set the API URL for production. Let's fix this:

### Step 7: Set Production API URL (Critical!)
We need to tell the frontend where to find your backend in production.

#### Option A: Using .env.production (Recommended)
1. Create file: `frontend/.env.production`
2. Add this line:
   ```
   VITE_API_URL=https://weather-forecast-backend-iknr.onrender.com
   ```
3. Save the file
4. Rebuild and redeploy:
   ```bash
   "C:\Program Files\nodejs\npm.cmd" run build
   "C:\Program Files\nodejs\npm.cmd" run deploy
   ```

#### Option B: Update vite.config.js (Alternative)
1. Open `frontend/vite.config.js`
2. Change the define section to:
   ```javascript
   define: {
     __API_BASE__: JSON.stringify(process.env.VITE_API_URL || 'https://weather-forecast-backend-iknr.onrender.com')
   }
   ```
3. Save
4. Rebuild and redeploy

### Why This Is Needed:
GitHub Pages serves static files from `https://PSubrat29.github.io/weather-forecast-app/`
When the frontend makes a request to `/weather`, it would go to:
`https://PSubrat29.github.io/weather-forecast-app/weather` (which doesn't exist)

By setting `VITE_API_URL`, we make it request:
`https://weather-forecast-backend-iknr.onrender.com/weather` (your live backend)

---

## 🚀 UPDATED DEPLOYMENT STEPS WITH API CONFIG

Let's do it properly:

### Step 1: Create .env.production
```bash
cd /d D:\ParidaUser\Claude-Project\weather-forecast-app\frontend
echo VITE_API_URL=https://weather-forecast-backend-iknr.onrender.com > .env.production
```

### Step 2: Rebuild Frontend
```bash
"C:\Program Files\nodejs\npm.cmd" run build
```

### Step 3: Redeploy to GitHub Pages
```bash
"C:\Program Files\nodejs\npm.cmd" run deploy
```

### Step 4: Test Your Live App
Visit: `https://PSubrat29.github.io/weather-forecast-app/`
Click "Load Weather Data" button
You should see:
1. Weather data from your Render.com backend
2. Model prediction (will show "0" or similar - our demo model)
3. No errors

---

## ✅ VERIFICATION CHECKLIST
After deployment, verify:
- [ ] GitHub Pages shows your live site at `https://PSubrat29.github.io/weather-forecast-app/`
- [ ] Clicking "Load Weather Data" fetches data from your Render backend
- [ ] You see JSON weather data in the output
- [ ] You see a prediction value (even if it's 0 from demo model)
- [ ] No red error messages in the browser console (F12 → Console)
- [ ] Button works repeatedly (not stuck on "Loading")

---

## 🛠️ TROUBLESHOOTING

**Issue**: Button shows "Failed to fetch weather data" or network error
- **Fix**: 
  1. Open browser console (F12 → Console)
  2. Check the exact URL it's trying to fetch
  3. Should be: `https://weather-forecast-backend-iknr.onrender.com/weather`
  4. If it's trying to fetch from github.io, .env.production wasn't loaded correctly
  5. Re-check .env.production file exists and has correct URL
  6. Rebuild and redeploy

**Issue**: Blank page or "Cannot GET /"
- **Fix**: 
  1. Verify GitHub Pages is set to `gh-pages` branch in Settings → Pages
  2. Wait 1-2 minutes after enabling Pages
  3. Clear browser cache or try incognito mode

**Issue**: Model fails to load (404 on model files)
- **Fix**: 
  1. Verify files exist in `frontend/public/model/` on GitHub
  2. Check that they were included in the build (look in `dist/` folder)
  3. Redeploy if needed

**Issue**: Button stays stuck on "Loading..."
- **Fix**:
  1. Backend might be sleeping (Render free tier sleeps after 15 min inactive)
  2. Wait 10-20 seconds for it to spin up
  3. Try again - subsequent requests will be fast

---

## 🎯 YOU'RE DONE!
Your full stack is now live:
- **Frontend**: `https://PSubrat29.github.io/weather-forecast-app/`
- **Backend**: `https://weather-forecast-backend-iknr.onrender.com/weather`

The app will:
1. Fetch real-time weather data from Open-Meteo via your Render backend
2. Run it through your TensorFlow.js model (demo version)
3. Display both raw data and prediction
4. Work for anyone, anywhere - completely free

---

## 🔄 UPDATING YOUR APPLICATION
To make changes:
1. **Frontend changes**:
   - Edit files in `frontend/`
   - `"C:\Program Files\nodejs\npm.cmd" run build`
   - `"C:\Program Files\nodejs\npm.cmd" run deploy`
2. **Backend changes**:
   - Edit files in `backend/`
   - `git add . && git commit -m "Your message"`
   - `git push origin main`
   - Render auto-deploys (watch logs in Render dashboard)
3. **Model updates**:
   - Replace files in `frontend/public/model/`
   - Rebuild and redeploy frontend

**Ready to test?** Follow the steps above to configure .env.production, rebuild, redeploy, then test your live app. Let me know when you see weather data and a prediction!