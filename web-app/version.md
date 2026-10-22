# Version history

## Unreleased

### Added
- Local web application interface for silence cutting across audio and video media.
- Two-color monochrome interface using black and white palette.
- Chunked octet-stream upload pipeline supporting media files up to 500 MB.
- Sound power cutoff slider to cut zones where sound power falls below threshold.
- Synchronized video and audio frame cutting with selectable quality presets.
- Pre-flight silence scanner displaying original duration, power metrics, and estimated time savings.
- REST endpoints for upload, scan, render, status polling, and download.
- Defensive security hardening with path sanitization, size limits, and security headers.
- Multi-stage Linux Dockerfile with non-root security context and embedded FFmpeg binaries.
- Render Blueprint configuration (`render.yaml`) for one-click web service deployment.
- Vercel configuration (`vercel.json`) with edge static hosting and API proxy rewrites.
- Cross-Origin Resource Sharing (CORS) preflight support and configurable origins via environment variables.
- Comprehensive deployment guide in `DEPLOYMENT.md`.
