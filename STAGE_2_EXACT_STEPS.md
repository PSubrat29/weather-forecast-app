# STAGE 2: EXACT RENDER.COM BACKEND DEPLOYMENT STEPS
## Follow these steps precisely to deploy your backend

You have successfully pushed code to: `https://github.com/PSubrat29/weather-forecast-app`

---

## ✅ PRE-CHECKLIST - VERIFY THESE FIRST
Before starting Render.com deployment, confirm:
1. [ ] Your GitHub repo is at: `https://github.com/PSubrat29/weather-forecast-app`
2. [ ] `backend/main.py` exists and contains the Open-Meteo API URL
3. [ ] `backend/requirements.txt` has:
   ```
   fastapi==0.136.0
   uvicorn==0.44.0
   httpx==0.28.1
   ```
4. [ ] You are logged into GitHub in your browser

---

## 🚀 STEP-BY-STEP INSTRUCTIONS

### 🔹 STEP 1: OPEN RENDER.COM
1. In your browser, go to: **https://render.com**
2. Click **"Sign Up"** (top right)
3. Choose **"Continue with GitHub"**
4. If prompted, authorize Render to access your repositories
5. You should now be logged in to Render.com

### 🔹 STEP 2: CREATE NEW WEB SERVICE
1. Once logged in, look for the **+ New +** button (usually top left or center)
2. Click it, then select **"Web Service"** from the menu
3. You should now see the "Create a Web Service" form

### 🔹 STEP 3: CONNECT YOUR REPOSITORY
1. In the "Connect a repository" section:
2. You should see a list of your GitHub repositories
3. Find and click on: **`PSubrat29/weather-forecast-app`**
4. If you don't see it:
   - Click **"Connect a new repository"**
   - Search for `weather-forecast-app`
   - Select it when it appears

### 🔹 STEP 4: FILL IN THE FORM EXACTLY
Complete each field as specified below:

#### **Name Field**
- Type: `weather-forecast-backend`
- This will be part of your URL

#### **Region Field** 
- Select: `US` (United States)
- *Choose EU if your users are primarily in Europe*

#### **Branch Field**
- Should automatically show: `main`
- If not, select `main` from dropdown

#### **Build Command Field**
- Click inside the field
- Type exactly: `pip install -r requirements.txt`
- Verify spelling and spacing

#### **Start Command Field**
- Click inside the field
- Type exactly: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Verify spelling, spacing, and the `$PORT` variable

#### **Environment Field**
- Click the dropdown
- Select: `Python 3`

#### **Plan Field**
- Should automatically show: `Free`
- If not, select `Free` from pricing options

### 🔹 STEP 5: OPTIONAL - ADVANCED SETTINGS
Scroll down to find the "Advanced" section (may be collapsed):
1. Click to expand "Advanced" if needed
2. **Auto-Deploy**: Ensure the toggle is **ON** (enabled)
   - This means your backend will automatically update when you push to GitHub
3. **Branch Deploys**: Ensure the toggle is **ON** (enabled)
   - This creates preview deployments for branches
4. **Health Check Path**: You can optionally type `/weather`
   - This helps Render know when your service is healthy
5. **Environment Variables**: Leave blank (we don't need any for this app)

### 🔹 STEP 6: CREATE THE SERVICE
1. Scroll to the bottom of the form
2. Find the green button labeled: **"Create Web Service"**
3. Click this button **once**
4. Render will immediately begin the deployment process

### 🔹 STEP 7: MONITOR THE DEPLOYMENT LOGS
You will now see a live log display. Watch for these stages in order:

1. **Cloning repository** 
   - Message: "Cloning into 'weather-forecast-app'..."
   - This means Render is downloading your code from GitHub

2. **Installing dependencies**
   - Message: "Collecting fastapi==0.136.0" etc.
   - This runs your `pip install -r requirements.txt` command
   - Should take 30-60 seconds

3. **Building**
   - Message: "Building..." or similar
   - Render prepares your application

4. **Starting service**
   - Message: "Starting service..."
   - This runs your `uvicorn main:app --host 0.0.0.0 --port $PORT` command

5. **Application startup complete**
   - Message: "Uvicorn running on http://0.0.0.0:PORT" 
   - This means your backend is ready!

### 🔹 STEP 8: WAIT FOR COMPLETION
- **Do not close this tab or navigate away**
- Deployment typically takes **2-4 minutes**
- You will know it's complete when you see:
  - A green banner at the top saying: **"✅ Web Service Live"**
  - Your service URL displayed (e.g., `https://weather-forecast-backend.onrender.com`)
  - The logs show "Application startup complete" without errors

### 🔹 STEP 9: TEST YOUR BACKEND IMMEDIATELY
Once you see the "✅ Web Service Live" banner:

1. **Click on your service URL** (it should be a clickable link)
   - OR manually visit: `https://weather-forecast-backend.onrender.com/weather`
   - (Note: Your exact subdomain might be slightly different - use what's shown)

2. **You should see JSON weather data** in your browser, similar to:
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
         "time": "2026-04-22T14:30",
         "interval": 900,
         "temperature": 15.2,
         "windspeed": 8.7,
         "winddirection": 220,
         "is_day": 1,
         "weathercode": 3
       }
     }
   }
   ```

3. **If you see this JSON data, your backend is successfully deployed!**

---

## ✅ VERIFICATION CHECKLIST
After completing the above steps, verify:
- [ ] Service status shows "Live" in Render dashboard
- [ ] Visiting `/weather` endpoint returns valid JSON (not an error page)
- [ ] No red error messages in the deployment logs
- [ ] Response loads within 2-3 seconds (first load may be slower)
- [ ] JSON contains temperature, windspeed, and other weather data

---

## 🛠️ IF YOU ENCOUNTER ISSUES

**"Build failed" error:**
1. Check the logs for specific error messages
2. Most common: `requirements.txt` typo or formatting
3. Fix locally, push to GitHub, Render will auto-rebuild

**"Service failed to start" error:**
1. Double-check your start command: 
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Most common: Missing `$PORT` or wrong host/port
3. Edit service settings → Save → Trigger manual deploy

**Seeing "Application error" in browser:**
1. First request after deployment can take 10-20 seconds (service waking up)
2. Wait 15 seconds and refresh
3. Free Render services sleep after 15 min of inactivity - this is normal

**404 Not Found on `/weather`:**
1. Confirm `backend/main.py` has: `@app.get("/weather")`
2. Ensure file is in `backend/` folder (not root)
3. Check GitHub to verify file wasn't moved or renamed

---

## 🎯 YOU'RE NOW READY FOR STAGE 3!
Once you have verified your backend is returning weather data at the `/weather` endpoint:

1. **Reply here with:** "Stage 2 complete - backend is live at [your-url]"
2. I will immediately provide **Stage 3**: Exact GitHub Pages frontend deployment steps
3. Then we will test your full live application
4. Finally, I'll show you how to update and maintain both deployments

**Your turn:** Go to Render.com now and follow these exact steps. Let me know when you see the green "✅ Web Service Live" banner and can access your `/weather` endpoint!