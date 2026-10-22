# Description: main.py

## Overview
Web application entry point validating FFmpeg runtime dependencies, creating the `ThreadingHTTPServer` socket, and binding to local host and port.

## Exports & Functions
- `verify_dependencies() -> bool`
  - **Description**: Verifies `ffmpeg` and `ffprobe` binaries are available in system PATH.
  - **Parameters**: None.
  - **Returns**: True if found, False otherwise.
- `main() -> None`
  - **Description**: Initializes and runs the HTTP server loop.
  - **Parameters**: None.
  - **Returns**: None.

## Dependencies & Data Flow
- **Imports**: `shutil`, `sys`, `http.server.ThreadingHTTPServer`, `config.*`, `server_router.DeadAirHTTPHandler`.
- **Invoked By**: Direct command line execution (`python main.py`).
- **Data Flow**: System PATH check -> socket bind -> hands control to `DeadAirHTTPHandler`.
