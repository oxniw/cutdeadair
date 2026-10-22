# Description: Dockerfile

## Overview
Container specification packaging Python 3.12, system FFmpeg binaries, and the CutDeadAir web application into a hardened, non-root Linux container for production deployments on Render.

## Key Directives
- `FROM python:3.12-slim`: Minimal Debian-based base image to reduce attack surface and build time.
- `RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates`: Installs the required FFmpeg/FFprobe binaries without extraneous suggested packages.
- `RUN useradd -m -u 10001 -s /bin/bash appuser`: Creates an unprivileged user (UID 10001) to eliminate root process execution risks.
- `USER appuser`: Switches context away from root before starting the server.
- `EXPOSE 8080`: Documents the listening container port.
- `CMD ["python", "main.py"]`: Direct process entry point running the standard library HTTP server.

## Dependencies & Data Flow
- **Base Image**: Debian Linux (Bookworm slim) / Python 3.12.
- **External Binaries**: FFmpeg, FFprobe.
- **Execution Target**: Render Web Services, local Docker engines, or Kubernetes pods.
