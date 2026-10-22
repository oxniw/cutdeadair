# About this project

## Purpose
A web-based silence and dead air removal tool that processes uploaded audio and video files through a browser interface or containerized cloud deployment.

## Audience
Creators, editors, and educators who need browser-based silence cutting without installing desktop graphical dependencies.

## Product scope
- **Audio and Video Processing**: Slices dead air from audio files and synchronizes cuts across video frames for MP4, MKV, MOV, and common media containers.
- **Sound Power Cutoff Slider**: Cuts any zone where audio sound power falls below the specified decibel threshold.
- **Pre-Flight Inspection**: Measures mean power, peak power, silence intervals, and projected time savings before rendering.
- **Audio Extraction**: Extracts trimmed audio tracks as MP3 directly from video inputs.
- **Two-Color Theme**: Minimal black and white user interface.
- **Cloud Deployment**: Production-ready deployment support for Render (Docker container) and Vercel (Edge static CDN with backend API proxy).

## Experience and theme
- **Visual Palette**: Strict two-color scheme using pure black (#000000) and pure white (#ffffff).
- **Typography & Layout**: High contrast borders, responsive grid layout, and real-time progress indicators.

## Technical constraints
- **Runtime**: Python 3.12 standard library.
- **External Binaries**: FFmpeg and FFprobe in system PATH or container environment.
- **Network**: HTTP service listening on dynamic `HOST` and `PORT` environment variables (default `0.0.0.0:8080`).
- **Zero External Python Dependencies**: Operates without pip packages.
- **Containerization**: Hardened Dockerfile executing as an unprivileged user (UID 10001).

## Quality, safety, and accessibility
- **Input Sanitization**: File names sanitized to prevent directory traversal attacks.
- **Size Caps**: Upload payloads capped at 500 MB to prevent resource exhaustion.
- **Defensive Headers**: Enforces Content Security Policy, nosniff, frame restriction, and CORS headers.
- **Isolated Processing**: Subprocess execution uses argument lists without shell interpolation.
