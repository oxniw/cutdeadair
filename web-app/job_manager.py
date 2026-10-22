# ==============================================================================
# File: .//Description-of-file/job_manager.md
# Overview: In-memory thread-safe state store tracking upload sessions, progress updates, and file cleanup.
# ==============================================================================

import os
import time
import threading
from typing import Dict, Any, Optional
from security import generate_secure_job_id

_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def create_job(filename: str, upload_path: str) -> str:
    """Initializes a new job entry with secure id and tracks input file path."""
    job_id = generate_secure_job_id()
    with _lock:
        _jobs[job_id] = {
            "id": job_id,
            "filename": filename,
            "upload_path": upload_path,
            "output_path": None,
            "status": "uploaded",
            "progress": 0.0,
            "message": "File uploaded successfully.",
            "scan_result": None,
            "summary": None,
            "created_at": time.time(),
            "error": None,
        }
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Returns a snapshot of the job dict if present."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            return dict(job)
        return None


def update_job(job_id: str, **kwargs) -> None:
    """Thread-safe update of job properties."""
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(kwargs)


def delete_job(job_id: str) -> None:
    """Removes a job and cleans up associated temporary files on disk."""
    with _lock:
        job = _jobs.pop(job_id, None)

    if job:
        for key in ("upload_path", "output_path"):
            path = job.get(key)
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def cleanup_expired_jobs(max_age_seconds: int = 3600) -> None:
    """Purges jobs and storage files older than max_age_seconds."""
    now = time.time()
    expired_ids = []

    with _lock:
        for j_id, data in _jobs.items():
            if now - data.get("created_at", 0) > max_age_seconds:
                expired_ids.append(j_id)

    for j_id in expired_ids:
        delete_job(j_id)
