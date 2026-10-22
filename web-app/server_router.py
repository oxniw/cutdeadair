# ==============================================================================
# File: .//Description-of-file/server_router.md
# Overview: HTTP request handler and API router enforcing defensive security headers, stream validation, and REST endpoints.
# ==============================================================================

import os
import json
import urllib.parse
import threading
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any

from config import (
    TEMP_UPLOAD_DIR,
    TEMP_PROCESSED_DIR,
    MAX_UPLOAD_SIZE_BYTES,
    SUPPORTED_EXTENSIONS,
    CORS_ALLOWED_ORIGINS,
)
from security import (
    sanitize_filename,
    validate_file_extension,
    validate_file_size,
    get_security_headers,
)
from domain_models import ProcessingSettings
from process_media import scan_media, process_media
from job_manager import create_job, get_job, update_job, delete_job


class DeadAirHTTPHandler(BaseHTTPRequestHandler):
    """Secure multi-threaded HTTP handler serving static assets and REST API endpoints."""

    def _send_security_headers(self) -> None:
        """Injects mandatory security headers into every response."""
        for header, val in get_security_headers(CORS_ALLOWED_ORIGINS).items():
            self.send_header(header, val)

    def _send_json(self, status: int, data: Dict[str, Any]) -> None:
        """Sends a JSON response with security headers."""
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, status: int, message: str) -> None:
        """Sends a structured JSON error response."""
        self._send_json(status, {"error": message})

    def do_GET(self) -> None:
        """Handles static file serving, job status queries, and file downloads."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_static("index.html", "text/html")
        elif path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            safe_name = sanitize_filename(rel_path)
            content_type = "text/plain"
            if safe_name.endswith(".css"):
                content_type = "text/css"
            elif safe_name.endswith(".js"):
                content_type = "application/javascript"
            elif safe_name.endswith(".html"):
                content_type = "text/html"
            self._serve_static(safe_name, content_type)
        elif path.startswith("/api/status/"):
            job_id = path[len("/api/status/"):].strip()
            job = get_job(job_id)
            if not job:
                self._send_error(404, "Job not found.")
                return
            clean_job = {
                "id": job["id"],
                "status": job["status"],
                "progress": job["progress"],
                "message": job["message"],
                "error": job["error"],
                "summary": {
                    "original_duration": job["summary"].original_duration,
                    "processed_duration": job["summary"].processed_duration,
                    "time_saved": job["summary"].time_saved,
                } if job.get("summary") else None,
            }
            self._send_json(200, clean_job)
        elif path.startswith("/api/download/"):
            job_id = path[len("/api/download/"):].strip()
            self._handle_download(job_id)
        else:
            self._send_error(404, "Resource not found.")

    def do_POST(self) -> None:
        """Handles uploads, pre-flight scans, and render trigger actions."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/upload":
            self._handle_upload()
        elif path.startswith("/api/scan/"):
            job_id = path[len("/api/scan/"):].strip()
            self._handle_scan(job_id)
        elif path.startswith("/api/process/"):
            job_id = path[len("/api/process/"):].strip()
            self._handle_process(job_id)
        else:
            self._send_error(404, "Endpoint not found.")

    def do_OPTIONS(self) -> None:
        """Handles cross-origin preflight requests with permissive security headers."""
        self.send_response(204)
        self._send_security_headers()
        self.end_headers()

    def do_DELETE(self) -> None:
        """Handles job cancellation and file cleanup."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/job/"):
            job_id = path[len("/api/job/"):].strip()
            delete_job(job_id)
            self._send_json(200, {"success": True})
        else:
            self._send_error(404, "Endpoint not found.")

    def _serve_static(self, filename: str, content_type: str) -> None:
        """Safely reads and serves static files from static directory."""
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        full_path = os.path.join(static_dir, filename)

        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            self._send_error(404, "File not found.")
            return

        with open(full_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def _handle_upload(self) -> None:
        """Streams uploaded octet-stream directly into isolated storage."""
        raw_filename = self.headers.get("X-Filename", "audio.mp3")
        filename = sanitize_filename(urllib.parse.unquote(raw_filename))

        if not validate_file_extension(filename, SUPPORTED_EXTENSIONS):
            self._send_error(400, f"Unsupported file extension. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}")
            return

        content_length_str = self.headers.get("Content-Length", "0")
        try:
            content_length = int(content_length_str)
        except ValueError:
            self._send_error(400, "Invalid Content-Length.")
            return

        if not validate_file_size(content_length, MAX_UPLOAD_SIZE_BYTES):
            self._send_error(413, f"Payload too large. Maximum size is {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB.")
            return

        os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
        temp_dest = os.path.join(TEMP_UPLOAD_DIR, f"{os.urandom(8).hex()}_{filename}")

        remaining = content_length
        chunk_size = 64 * 1024

        with open(temp_dest, "wb") as f:
            while remaining > 0:
                read_bytes = min(remaining, chunk_size)
                chunk = self.rfile.read(read_bytes)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        if remaining > 0:
            if os.path.exists(temp_dest):
                os.remove(temp_dest)
            self._send_error(400, "Incomplete upload stream.")
            return

        job_id = create_job(filename, temp_dest)
        self._send_json(200, {"job_id": job_id, "filename": filename, "size": content_length})

    def _read_json_body(self) -> Dict[str, Any]:
        """Safely parses JSON request body."""
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len <= 0 or content_len > 1024 * 1024:
            return {}
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def _parse_settings(self, data: Dict[str, Any]) -> ProcessingSettings:
        """Parses and bounds-checks client request settings."""
        quality_map = {
            "High Quality (CRF 18)": ("medium", 18),
            "Fast (CRF 22)": ("fast", 22),
            "Compact (CRF 26)": ("fast", 26),
            "Draft (Ultrafast)": ("ultrafast", 24),
        }
        quality_str = str(data.get("video_quality", "Fast (CRF 22)"))
        preset, crf = quality_map.get(quality_str, ("fast", 22))

        return ProcessingSettings(
            threshold_db=max(-70.0, min(-5.0, float(data.get("threshold_db", -32.0)))),
            min_silence_duration=max(0.05, min(3.0, float(data.get("min_silence_duration", 0.6)))),
            margin_padding=max(0.0, min(0.5, float(data.get("margin_padding", 0.15)))),
            target_pause=max(0.05, min(0.8, float(data.get("target_pause", 0.3)))),
            mode="cut" if data.get("mode") == "cut" else "shorten",
            export_audio_only=bool(data.get("export_audio_only", False)),
            video_preset=preset,
            video_crf=crf,
        )

    def _handle_scan(self, job_id: str) -> None:
        """Runs pre-flight audio analysis and returns metrics."""
        job = get_job(job_id)
        if not job or not os.path.exists(job["upload_path"]):
            self._send_error(404, "Job or media file not found.")
            return

        settings = self._parse_settings(self._read_json_body())

        try:
            scan_res = scan_media(job["upload_path"], settings)
            update_job(job_id, scan_result=scan_res)

            self._send_json(200, {
                "total_duration": scan_res.total_duration,
                "total_silence_duration": scan_res.total_silence_duration,
                "silence_count": len(scan_res.silence_intervals),
                "estimated_output_duration": scan_res.estimated_output_duration,
                "time_saved": scan_res.time_saved,
                "percentage_saved": scan_res.percentage_saved,
                "mean_power_db": scan_res.mean_power_db,
                "max_power_db": scan_res.max_power_db,
                "is_video": scan_res.is_video,
            })
        except Exception as err:
            self._send_error(500, f"Analysis failed: {err}")

    def _handle_process(self, job_id: str) -> None:
        """Spawns background rendering worker."""
        job = get_job(job_id)
        if not job or not os.path.exists(job["upload_path"]):
            self._send_error(404, "Job or media file not found.")
            return

        if job["status"] == "processing":
            self._send_json(200, {"status": "processing"})
            return

        settings = self._parse_settings(self._read_json_body())
        update_job(job_id, status="processing", progress=0.05, message="Starting render...")

        def worker():
            try:
                os.makedirs(TEMP_PROCESSED_DIR, exist_ok=True)
                root_name, ext = os.path.splitext(job["filename"])
                if settings.export_audio_only and job.get("scan_result") and job["scan_result"].is_video:
                    ext = ".mp3"
                out_filename = f"{root_name}_cut{ext}"
                out_path = os.path.join(TEMP_PROCESSED_DIR, f"{job_id}_{out_filename}")

                def progress_cb(frac: float, msg: str):
                    update_job(job_id, progress=frac, message=msg)

                summary = process_media(
                    file_path=job["upload_path"],
                    output_path=out_path,
                    settings=settings,
                    scan_result=job.get("scan_result"),
                    progress_callback=progress_cb,
                )

                if summary.success:
                    update_job(
                        job_id,
                        status="done",
                        progress=1.0,
                        message="Complete!",
                        output_path=out_path,
                        summary=summary,
                    )
                else:
                    update_job(
                        job_id,
                        status="failed",
                        error=summary.error_message or "Render failed",
                    )
            except Exception as err:
                update_job(job_id, status="failed", error=str(err))

        threading.Thread(target=worker, daemon=True).start()
        self._send_json(200, {"status": "started", "job_id": job_id})

    def _handle_download(self, job_id: str) -> None:
        """Streams processed media file with Content-Disposition attachment."""
        job = get_job(job_id)
        if not job or not job.get("output_path") or not os.path.exists(job["output_path"]):
            self._send_error(404, "Processed file not available for download.")
            return

        file_path = job["output_path"]
        file_size = os.path.getsize(file_path)
        root_name, ext = os.path.splitext(job["filename"])
        if file_path.endswith(".mp3"):
            ext = ".mp3"
        safe_download_name = f"{root_name}_cut{ext}"

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(file_size))
        self.send_header("Content-Disposition", f'attachment; filename="{safe_download_name}"')
        self._send_security_headers()
        self.end_headers()

        with open(file_path, "rb") as f:
            chunk_size = 64 * 1024
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.wfile.write(chunk)
