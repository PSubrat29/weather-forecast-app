# Weather Forecast App - Deployment Guide

## Option 1: GitHub Pages + Render.com (Recommended)

This guide walks you through deploying the frontend to GitHub Pages and the backend to Render.com.

## STAGE 1: PREPARATION & GITHUB SETUP
*(Complete these steps on your local machine)*

### Step 1: Initialize Git Repository (if not already done)
```bash
# Navigate to your project directory
cd D:\ParidaUser\Claude-Project\weather-forecast-app

# Initialize git repository
git init

# Configure your identity (if not already set)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Weather forecast app with working model and free APIs"
```

### Step 2: Create GitHub Repository
1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon in the top-right → "New repository"
3. Repository name: `weather-forecast-app` (or your preferred name)
4. Description: "Weather forecast dashboard with real-time data and TensorFlow.js predictions"
5. Choose "Public" (free for GitHub Pages)
6. ✅ Initialize with a README (optional - we already have one)
7. Click "Create repository"

### Step 3: Connect Local Repository to GitHub
```bash
# Add the remote origin (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/weather-forecast-app.git

# Push to main branch
git branch -M main
git push -u origin main
```

### Step 4: Verify GitHub Setup
1. Go to your GitHub repository page
2. Verify all files are present:
   - backend/main.py
   - frontend/src/components/Weather.vue
   - frontend/public/model/model.json
   - frontend/public/model/group1-shard1of1
   - README.md
   - .gitignore

### Step 5: Prepare for Backend Deployment (Render.com)
Ensure these files are correctly configured:
1. **backend/main.py** - Uses free Open-Meteo API (no keys needed)
2. **backend/requirements.txt** - Contains:
   ```
   fastapi==0.136.0
   uvicorn==0.44.0
   httpx==0.28.1
   ```
3. **No .env file needed** - API is free and key-less

### Step 6: Prepare for Frontend Deployment (GitHub Pages)
1. **frontend/vite.config.js** - Already configured for proxying
2. **Build command** will be: `npm run build`
3. **Output directory** will be: `dist/`

### Step 7: Test Locally One More Time
```bash
# In one terminal - start backend
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# In another terminal - start frontend
cd frontend
..\..\..\..\Program Files\nodejs\npm.cmd run dev
```

Visit http://localhost:5173 and click "Load Weather Data" to verify everything works.

## STAGE 2: BACKEND DEPLOYMENT (RENDER.COM)
*(To be completed after Stage 1)*

### Step 1: Sign up/Log in to Render.com
1. Go to [render.com](https://render.com)
2. Sign up using GitHub (recommended) or email

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub account if prompted
3. Select the `weather-forecast-app` repository
4. Configure:
   - **Name**: weather-forecast-backend (or similar)
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### Step 3: Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the server
3. Wait for deployment to complete (2-3 minutes)
4. Note the URL provided (e.g., `https://weather-forecast-backend.onrender.com`)

### Step 4: Test Backend
Visit `https://your-backend-url.onrender.com/weather` in your browser
You should see JSON weather data from Open-Meteo API.

## STAGE 3: FRONTEND DEPLOYMENT (GITHUB PAGES)
*(To be completed after Stage 2)*

### Step 1: Build Frontend Locally
```bash
cd frontend
..\..\..\..\Program Files\nodejs\npm.cmd run build
```
This creates a `dist/` directory with production-ready files.

### Step 2: Deploy to GitHub Pages
**Option A: Using GitHub Actions (Recommended)**
1. The workflow will be set up automatically in later steps
2. Push to main branch triggers build and deploy

**Option B: Manual Deploy to gh-pages branch**
```bash
# Install gh-pages tool (if not already installed)
..\..\..\..\Program Files\nodejs\npm.cmd install --save-dev gh-pages

# Add to package.json scripts:
# "deploy": "gh-pages -d dist"

# Deploy
..\..\..\..\Program Files\nodejs\npm.cmd run deploy
```

**Option C: Using /docs folder**
1. Move contents of `dist/` to `/docs` folder
2. Commit and push
3. In GitHub repo Settings → Pages → Source: `/docs` folder

### Step 3: Configure API Endpoint for Production
The frontend automatically handles this:
- In development: Uses Vite proxy (`/weather` → `http://localhost:8000/weather`)
- In production: Uses relative `/weather` endpoint (same domain as frontend)

No code changes needed!

### Step 4: Test Live Deployment
1. Visit your GitHub Pages URL: `https://USERNAME.github.io/weather-forecast-app/`
2. Click "Load Weather Data"
3. Verify:
   - Weather data loads from your Render.com backend
   - Model prediction displays (will show "0" since we used zero weights - replace with real model later)
   - No errors in browser console

## STAGE 4: POST-DEPLOYMENT
*(Optional enhancements)*

### Update Model with Real Weights
When you have a trained TensorFlow.js model:
1. Replace `frontend/public/model/model.json` and `frontend/public/model/group1-shard1of1`
2. Commit and push
3. Redeploy frontend

### Custom Domain (Optional)
- Render.com: Add custom domain in service settings
- GitHub Pages: Add custom domain in repo Settings → Pages

### Environment Variables (if needed in future)
- Render.com: Set in Service → Environment
- GitHub Pages: Use public variables only (or configure backend to handle secrets)

## Troubleshooting

### Backend Issues
- **Port already in use**: Render handles this automatically with `$PORT`
- **Dependencies not installing**: Check requirements.txt format
- **Application errors**: Check Render.com logs

### Frontend Issues
- **Blank page**: Check GitHub Pages URL matches base in vite.config.js
- **Model not loading**: Verify files are in `public/model/` and accessible
- **API calls failing**: Check browser console for CORS or network errors

## Security Notes
✅ **No API keys exposed** - Using free Open-Meteo API
✅ **No secrets in frontend** - Model is public anyway
✅ **HTTPS enforced** - Both Render.com and GitHub Pages provide HTTPS
✅ **Regular updates** - Dependencies can be updated via npm/pip

## Next Steps
1. Complete Stage 1 steps above
2. Move to Stage 2 (Render.com deployment)
3. Complete Stage 3 (GitHub Pages deployment)
4. Share your live URLs!

Happy coding! 🌤️