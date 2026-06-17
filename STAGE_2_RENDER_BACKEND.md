# STAGE 2: RENDER.COM BACKEND DEPLOYMENT
## Exact Step-by-Step Instructions

You have successfully pushed your code to GitHub at:
`https://github.com/PSubrat29/weather-forecast-app`

Now let's deploy the backend to Render.com.

---

## 📋 PRE-FLIGHT CHECK (Verify before starting)
Make sure these are correct in your GitHub repo:
- [ ] `backend/main.py` exists and uses Open-Meteo API
- [ ] `backend/requirements.txt` contains:
  ```
  fastapi==0.136.0
  uvicorn==0.44.0
  httpx==0.28.1
  ```
- [ ] No `.env` file is needed (API is free and key-less)
- [ ] Your GitHub repo is public

---

## 🚀 STEP-BY-STEP RENDER.COM DEPLOYMENT

### Step 1: Sign In to Render.com
1. Go to [https://render.com](https://render.com)
2. Click **"Sign Up"** → Choose **"Continue with GitHub"** (recommended)
3. Authorize Render to access your GitHub account (select the `weather-forecast-app` repo)
4. You'll be logged in automatically

### Step 2: Create New Web Service
1. Once logged in, click the **+ New +** button in the top navigation
2. Select **"Web Service"** from the dropdown menu
3. On the "Create a Web Service" page:

### Step 3: Connect Your Repository
1. Under **"Connect a repository"**, you should see your GitHub repositories
2. Find and select: **`PSubrat29/weather-forecast-app`**
3. If you don't see it, click **"Connect a new repository"** and search for it

### Step 4: Configure the Service
Fill in the form exactly as follows:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `weather-forecast-backend` | This will be part of your URL |
| **Region** | `US` (or closest to your users) | Choose US, EU, etc. |
| **Branch** | `main` | Should be auto-selected |
| **Build Command** | `pip install -r requirements.txt` | **Type this exactly** |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` | **Type this exactly** |
| **Environment** | `Python 3` | Select from dropdown |
| **Plan** | `Free` | Should be auto-selected |

### Step 5: Advanced Settings (Optional but Recommended)
Scroll down to **"Advanced"** section and click to expand:
- **Auto-Deploy**: ✅ **Enabled** (so it rebuilds when you push to GitHub)
- **Branch Deploys**: ✅ **Enabled** (for preview deployments)
- **Health Check Path**: `/weather` (optional but good practice)
- **Environment**: Leave blank (no secrets needed for this app)

### Step 6: Create the Web Service
1. Click the **"Create Web Service"** button at the bottom
2. Render will immediately start the deployment process

### Step 7: Watch the Deployment Logs
You'll see a live log stream with these stages:
1. **Cloning repository** - Render downloads your code from GitHub
2. **Installing dependencies** - Runs `pip install -r requirements.txt`
3. **Building** - Prepares the application
4. **Starting service** - Runs your start command
5. **Application startup complete** - Success!

### Step 8: Wait for Completion
- Deployment typically takes **2-3 minutes**
- Do not close the tab or navigate away until you see:
  ```
  ✅ Web Service Live
  ```
- You'll see a green banner with your service URL (e.g., `https://weather-forecast-backend.onrender.com`)

### Step 9: Test Your Backend Immediately
Once deployed, click on your service URL or visit:
```
https://weather-forecast-backend.onrender.com/weather
```
(Replace with your actual subdomain if different)

You should see JSON weather data similar to:
```json
{
  "openmeteo": {
    "latitude": 52.52,
    "longitude": 13.419998,
    "generationtime_ms": 0.088,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 38.0,
    "current_weather_units": {
      "time": "iso8601",
      "interval": "seconds",
      "temperature": "°C",
      "windspeed": "km/h",
      "winddirection": "°",
      "is_day": "",
      "weathercode": "wmo code"
    },
    "current_weather": {
      "time": "2026-04-22T10:00",
      "interval": 900,
      "temperature": 14.5,
      "windspeed": 12.3,
      "winddirection": 280,
      "is_day": 1,
      "weathercode": 3
    }
  }
}
```

## 🔍 VERIFICATION CHECKLIST
After deployment, verify:
- [ ] Service shows "Live" status in Render dashboard
- [ ] Visiting `/weather` endpoint returns valid JSON
- [ ] No errors in the deployment logs
- [ ] Response time is reasonable (< 2 seconds typically)
- [ ] Data includes temperature, windspeed, etc. from Open-Meteo

## 🛠️ TROUBLESHOOTING COMMON ISSUES

**If you see "Build failed":**
1. Check the logs for specific error messages
2. Most common: `requirements.txt` formatting issues
3. Fix: Ensure each package is on its own line with exact versions
4. Push fix to GitHub → Render auto-rebuilds

**If you see "Service failed to start":**
1. Check start command: must be `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Most common: Forgetting `$PORT` or using wrong host/port
3. Fix: Update start command in service settings → Trigger manual deploy

**If you see "Application error" but logs show startup:**
1. First request after deployment can take 10-20 seconds (service spinning up)
2. Wait and refresh - free services spin down after 15 min of inactivity
3. This is normal for Render's free tier

**If you get 404 on `/weather`:**
1. Double-check your `backend/main.py` has `@app.get("/weather")` route
2. Ensure file is in `backend/` directory (not root)
3. Check GitHub to confirm file hasn't been moved

## 📝 IMPORTANT NOTES FOR RENDER.COM

### ✅ **Why this works for free:**
- Render's free tier provides:
  - 512 MB RAM
  - Shared CPU
  - Automatic HTTPS
  - GitHub integration
  - Auto-deploys on push
- More than sufficient for this low-traffic weather app

### 🔒 **Security:**
- No API keys or secrets needed (Open-Meteo is free and public)
- Render provides automatic HTTPS/SSL
- Your code remains private unless you make the repo public

### ⚡ **Performance:**
- First request after inactivity: 10-20 seconds (spin-up time)
- Subsequent requests: < 1 second
- Free services sleep after 15 minutes of inactivity
- This is normal and expected

### 🔄 **Updating Your Backend:**
1. Make changes locally to `backend/`
2. `git add . && git commit -m "Your message"`
3. `git push origin main`
4. Render automatically detects the push and redeploys
5. Watch the logs in your Render dashboard

## 🎯 YOU'RE DONE WITH STAGE 2!
Your backend is now live at:
`https://weather-forecast-backend.onrender.com/weather` (or your custom subdomain)

## 🚀 WHAT'S NEXT?
Once you confirm your backend is working (see verification above):
1. **Reply here saying "Stage 2 complete"**
2. I'll immediately provide **Stage 3**: Exact GitHub Pages frontend deployment steps
3. Then: How to test your full live app
4. Finally: How to update and maintain your deployment

**Ready to proceed?** Test your backend endpoint now and let me know when it's returning weather data!