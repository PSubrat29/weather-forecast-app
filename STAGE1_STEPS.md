# STAGE 1: PREPARATION & GITHUB SETUP
## Weather Forecast App - Deployment Preparation

Follow these exact steps to prepare your project for GitHub + Render.com deployment.

---

## ✅ PREREQUISITES CHECKLIST
Before starting, verify you have:
- [ ] Git installed (`git --version`)
- [ ] Node.js installed (`node --version` should be v16+)
- [ ] npm installed (`npm --version`)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] GitHub account

---

## 📋 STAGE 1 STEPS - DO THESE NOW

### Step 1: Open Command Prompt/Terminal
Press `Win + R`, type `cmd`, hit Enter (Windows)
OR open Terminal/PowerShell

### Step 2: Navigate to Your Project
```bash
cd /d D:\ParidaUser\Claude-Project\weather-forecast-app
```

### Step 3: Initialize Git Repository
```bash
git init
git config --global user.name "Your GitHub Username"
git config --global user.email "your.email@example.com"
git add .
git commit -m "Initial commit: Weather forecast app with working model and free APIs"
```

### Step 4: Create GitHub Repository
1. Go to https://github.com
2. Click "+" → "New repository"
3. Repository name: `weather-forecast-app`
4. Description: "Weather forecast dashboard with real-time data and TensorFlow.js predictions"
5. ✅ Public (free for GitHub Pages)
6. ❌ Do NOT initialize with README (we already have one)
7. Click "Create repository"

### Step 5: Link Local to Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/weather-forecast-app.git
git branch -M main
git push -u origin main
```
Replace `YOUR_USERNAME` with your actual GitHub username

### Step 6: Verify Upload
1. Go to https://github.com/YOUR_USERNAME/weather-forecast-app
2. Refresh the page
3. Confirm you see:
   - `backend/main.py`
   - `frontend/src/components/Weather.vue`
   - `frontend/public/model/`
   - `README.md`
   - `.gitignore`

### Step 7: Final Local Test (Optional but Recommended)
```bash
# Start backend
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# In NEW terminal window:
cd frontend
"C:\Program Files\nodejs\npm.cmd" run dev
```
Then visit http://localhost:5173 and test the "Load Weather Data" button.

---

## 🎯 WHAT YOU'VE ACCOMPLISHED
✅ Code is safely backed up on GitHub
✅ Repository is ready for Render.com backend deployment
✅ Repository is ready for GitHub Pages frontend deployment
✅ All dependencies documented
✅ .gitignore prevents uploading unnecessary files

---

## 🚀 NEXT STEPS (STAGE 2)
After completing Stage 1:
1. **Backend Deployment**: Sign up at render.com → Create Web Service → Connect GitHub repo
2. **Frontend Deployment**: Build frontend → Deploy to GitHub Pages
3. **Test Live**: Visit your GitHub Pages URL and verify weather data loads

Keep this guide handy - you'll need it for Stage 2!