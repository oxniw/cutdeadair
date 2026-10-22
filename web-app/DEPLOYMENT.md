# Deployment Guide: CutDeadAir Web Application

This guide covers deployment to Render and Vercel.

---

## 1. Architecture Overview

- **Render (Full-Stack Container)**:
  Runs the Python web server and native FFmpeg binary in a hardened Linux container.
  Handles file uploads up to 500 MB and multi-minute video/audio rendering.
  Serves both the monochrome static frontend and the REST API.

- **Vercel (Static Frontend CDN) + Render (Backend API)**:
  Vercel hosts the static HTML, CSS, and client-side JavaScript.
  Vercel rewrites `/api/*` requests to your Render backend URL.
  Eliminates serverless timeouts while providing fast edge asset delivery.

---

## 2. Deploying to Render (Recommended)

### Prerequisites
- A free Render account at [render.com](https://render.com).
- A GitHub repository containing this project.

### Step-by-Step Instructions
1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Add CutDeadAir web application and deployment configuration"
   git push origin main
   ```

2. Log in to your Render Dashboard:
   - Click **New +** and select **Web Service**.
   - Connect your GitHub repository.

3. Configure the service:
   - **Name**: `cutdeadair` (or your choice)
   - **Region**: Oregon (or your preferred region)
   - **Runtime**: `Docker`
   - **Docker Context**: `./web-app` (or `.` if repo root is the web app)
   - **Dockerfile Path**: `./web-app/Dockerfile` (or `Dockerfile`)
   - **Instance Type**: `Free`

4. Environment Variables:
   Render sets `PORT` automatically. Ensure these variables are defined:
   - `HOST`: `0.0.0.0`
   - `CORS_ALLOWED_ORIGINS`: `*`

5. Click **Create Web Service**:
   - Render builds the Docker image and installs FFmpeg.
   - When the deploy finishes, your app is live at `https://cutdeadair-xxxx.onrender.com`.

---

## 3. Deploying Frontend to Vercel (Optional Edge CDN)

### Step-by-Step Instructions
1. First, deploy the backend to Render as shown above and copy your Render URL (for example: `https://cutdeadair.onrender.com`).

2. Update `web-app/vercel.json`:
   Replace `https://YOUR_RENDER_SERVICE.onrender.com` with your real Render URL:
   ```json
   {
     "version": 2,
     "cleanUrls": true,
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://cutdeadair.onrender.com/api/:path*"
       },
       {
         "source": "/static/:path*",
         "destination": "/static/:path*"
       },
       {
         "source": "/",
         "destination": "/static/index.html"
       }
     ]
   }
   ```

3. Deploy via Vercel CLI or Dashboard:
   - **Option A: Vercel CLI**:
     ```bash
     cd web-app
     npx vercel
     ```
   - **Option B: Vercel Dashboard**:
     - Connect your GitHub repository.
     - Set **Root Directory** to `web-app`.
     - Framework Preset: `Other`.
     - Click **Deploy**.

4. Your application frontend is now live on Vercel and routes all media processing tasks directly to Render.

---

## 4. Verification Checklist

1. Open your production URL in any web browser.
2. Confirm the monochrome UI loads with audio and video controls.
3. Upload a sample audio or video file.
4. Click **Scan Media** to verify FFprobe analysis.
5. Click **Cut Dead Air** to run the render pipeline.
6. Verify the cut media file downloads correctly.
