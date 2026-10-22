# Description: DEPLOYMENT.md

## Overview
Deployment reference guide detailing step-by-step procedures to deploy the CutDeadAir web application to Render (Docker web service) and Vercel (edge static hosting with API rewrites).

## Contents & Architecture
- **Render Deployment**: Single container deployment packaging Python 3.12, FFmpeg, and the frontend on Render free tier.
- **Vercel Deployment**: Edge CDN deployment using `vercel.json` rewrites to proxy `/api/*` endpoints to Render while serving static assets from edge locations.
- **Verification Checklist**: Operational steps to test file uploads, silence scanning, media rendering, and processed file downloads.

## Dependencies & Data Flow
- **Platforms**: Render, Vercel, GitHub.
- **Target Files**: `Dockerfile`, `render.yaml`, `vercel.json`.
