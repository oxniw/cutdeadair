# Description: server_router.py

## Overview
HTTP request handler and API router enforcing defensive security headers, stream validation, CORS preflight handling, and REST endpoints.

## Exports & Functions
- `class DeadAirHTTPHandler(BaseHTTPRequestHandler)`: Multi-threaded HTTP handler processing GET, POST, DELETE, and OPTIONS requests.
  - `_send_security_headers()`: Injects mandatory defensive and CORS security headers.
  - `do_OPTIONS()`: Responds to cross-origin preflight requests with 204 No Content.
  - `_serve_static(filename, content_type)`: Safely delivers HTML, CSS, and JS assets.
  - `_handle_upload()`: Streams uploaded file to isolated storage with size validation.
  - `_handle_scan(job_id)`: Dispatches pre-flight scan request.
  - `_handle_process(job_id)`: Launches background media rendering worker.
  - `_handle_download(job_id)`: Streams processed file with attachment header.

## Dependencies & Data Flow
- **Imports**: `os`, `json`, `urllib.parse`, `threading`, `http.server.BaseHTTPRequestHandler`, `config.*`, `security.*`, `domain_models.*`, `process_media.*`, `job_manager.*`.
- **Invoked By**: `main.py` via `ThreadingHTTPServer`.
- **Data Flow**: HTTP clients <-> REST API endpoints <-> pipeline workers and filesystem.
