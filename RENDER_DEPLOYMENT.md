# Render Deployment Instructions

## Backend Deployment

1. **Create Web Service on Render**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

2. **Configure Build Settings**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`

3. **Add Environment Variables**
   - `HUGGINGFACE_API_KEY` = `your_huggingface_api_key_here`
   - `GMAIL_USER` = `your_gmail@gmail.com` (optional)
   - `GMAIL_PASSWORD` = `your_app_password` (optional)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Copy your backend URL (e.g., `https://your-app.onrender.com`)

## Frontend Deployment

1. **Update API URL in Frontend**
   - Edit `frontend/src/App.js`
   - Replace `http://localhost:8000` with your Render backend URL

2. **Deploy Frontend**
   - Use Vercel, Netlify, or Render Static Site
   - Build command: `npm run build`
   - Publish directory: `build`

## Important Notes
- Render's free tier may spin down after inactivity (takes ~30s to wake up)
- The PORT environment variable is automatically provided by Render
- Backend MUST bind to `0.0.0.0` (not `127.0.0.1` or `localhost`)
