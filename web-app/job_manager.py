# ==============================================================================
# File: .//Description-of-file/job_manager.md
# Overview: Thread-safe and disk-persistent state store tracking upload sessions, progress updates, and file cleanup.
# ==============================================================================

import os  # Filesystem operations
import time  # Time tracking for expirations
import json  # JSON serialization for disk persistence
import threading  # Thread safety locks
from typing import Dict, Any, Optional  # Type annotations
from dataclasses import is_dataclass, asdict  # Dataclass helpers
from config import TEMP_JOBS_DIR  # Job metadata directory
from security import generate_secure_job_id, sanitize_filename  # Security utilities

_lock = threading.Lock()  # Reentrant synchronization lock
_jobs: Dict[str, Dict[str, Any]] = {}  # In-memory fast cache


def _get_job_file_path(job_id: str) -> str:
    """Returns the persistent JSON file path for a given job identifier."""
    safe_id = sanitize_filename(job_id)  # Sanitize to prevent path traversal
    return os.path.join(TEMP_JOBS_DIR, f"{safe_id}.json")  # Resolve full JSON file path


def _save_job_to_disk(job_data: Dict[str, Any]) -> None:
    """Persists job metadata dictionary to disk in JSON format."""
    try:  # Handle disk write safely
        os.makedirs(TEMP_JOBS_DIR, exist_ok=True)  # Ensure jobs directory exists
        path = _get_job_file_path(job_data["id"])  # Get file path
        # Convert non-serializable objects to dicts
        serializable = dict(job_data)  # Make a copy
        for key in ("summary", "scan_result"):  # Check dataclass fields
            val = serializable.get(key)  # Get value
            if val is not None and is_dataclass(val):  # If dataclass instance
                serializable[key] = asdict(val)  # Convert to plain dictionary
        with open(path, "w", encoding="utf-8") as f:  # Write JSON file
            json.dump(serializable, f, indent=2)  # Dump serializable dict
    except Exception:  # Ignore disk write issues gracefully
        pass  # Pass


def _load_job_from_disk(job_id: str) -> Optional[Dict[str, Any]]:
    """Loads job metadata from disk if present."""
    path = _get_job_file_path(job_id)  # Resolve path
    if not os.path.exists(path):  # Check existence
        return None  # Not found
    try:  # Read JSON file
        with open(path, "r", encoding="utf-8") as f:  # Open file
            data = json.load(f)  # Parse JSON
            return data  # Return parsed dict
    except Exception:  # Handle parse errors
        return None  # Return None on corruption


def create_job(filename: str, upload_path: str) -> str:
    """Initializes a new job entry with secure id and writes state to disk and memory."""
    job_id = generate_secure_job_id()  # Generate random 128-bit hex token
    job_record = {  # Create initial job record
        "id": job_id,  # Job identifier
        "filename": filename,  # Original file name
        "upload_path": upload_path,  # Local path to uploaded media
        "output_path": None,  # Output path populated on completion
        "status": "uploaded",  # Initial lifecycle state
        "progress": 0.0,  # Progress percentage (0.0 to 1.0)
        "message": "File uploaded successfully.",  # User-facing status message
        "scan_result": None,  # Pre-flight scan metrics
        "summary": None,  # Final processing summary
        "created_at": time.time(),  # Creation epoch timestamp
        "error": None,  # Error message if failed
    }  # End job record
    with _lock:  # Acquire thread lock
        _jobs[job_id] = job_record  # Store in memory cache
        _save_job_to_disk(job_record)  # Persist to disk
    return job_id  # Return generated job id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Returns a snapshot of the job dict from memory or disk, recovering from server restarts."""
    with _lock:  # Acquire thread lock
        job = _jobs.get(job_id)  # Check memory cache
        if job:  # If in memory
            return dict(job)  # Return memory snapshot

        # If not in memory, recover from disk
        disk_job = _load_job_from_disk(job_id)  # Load from disk
        if disk_job:  # If record exists on disk
            # If server restarted while job was actively processing, mark as failed
            if disk_job.get("status") == "processing":  # Inactive worker
                disk_job["status"] = "failed"  # Transition to failed
                disk_job["error"] = "The server restarted during rendering. Please retry."  # Informative error
                _save_job_to_disk(disk_job)  # Update disk record
            _jobs[job_id] = disk_job  # Restore into memory cache
            return dict(disk_job)  # Return restored job snapshot

        return None  # Job does not exist


def update_job(job_id: str, **kwargs) -> None:
    """Thread-safe update of job properties in memory and on disk."""
    with _lock:  # Acquire thread lock
        job = _jobs.get(job_id)  # Fetch from memory
        if not job:  # If not in memory, try loading from disk
            job = _load_job_from_disk(job_id)  # Load from disk
            if job:  # If found on disk
                _jobs[job_id] = job  # Cache in memory
        if job:  # If job exists
            job.update(kwargs)  # Update attributes
            _save_job_to_disk(job)  # Persist updated state to disk


def delete_job(job_id: str) -> None:
    """Removes a job, deletes disk metadata, and cleans up uploaded/processed files."""
    with _lock:  # Acquire thread lock
        job = _jobs.pop(job_id, None)  # Remove from memory
        if not job:  # If not in memory, check disk
            job = _load_job_from_disk(job_id)  # Load from disk
        # Remove JSON metadata file
        meta_path = _get_job_file_path(job_id)  # Resolve metadata file path
        if os.path.exists(meta_path):  # If file exists
            try:  # Remove metadata
                os.remove(meta_path)  # Delete JSON file
            except OSError:  # Ignore error
                pass  # Pass

    if job:  # If job record existed
        for key in ("upload_path", "output_path"):  # Check media files
            path = job.get(key)  # Get path
            if path and os.path.exists(path):  # If file on disk
                try:  # Attempt removal
                    os.remove(path)  # Delete media file
                except OSError:  # Ignore removal errors
                    pass  # Pass


def cleanup_expired_jobs(max_age_seconds: int = 3600) -> None:
    """Purges jobs and storage files older than max_age_seconds."""
    now = time.time()  # Current timestamp
    expired_ids = []  # List of expired job IDs

    with _lock:  # Acquire thread lock
        for j_id, data in list(_jobs.items()):  # Check memory items
            if now - data.get("created_at", 0) > max_age_seconds:  # If expired
                expired_ids.append(j_id)  # Mark for removal

    if os.path.exists(TEMP_JOBS_DIR):  # Check disk jobs directory
        for fname in os.listdir(TEMP_JOBS_DIR):  # Iterate disk files
            if fname.endswith(".json"):  # Match JSON files
                j_id = fname[:-5]  # Strip extension
                if j_id not in expired_ids:  # If not already marked
                    meta_path = os.path.join(TEMP_JOBS_DIR, fname)  # Full path
                    try:  # Check file modification time
                        mtime = os.path.getmtime(meta_path)  # File mtime
                        if now - mtime > max_age_seconds:  # If expired
                            expired_ids.append(j_id)  # Mark for deletion
                    except OSError:  # Handle error
                        pass  # Pass

    for j_id in expired_ids:  # Clean up all expired jobs
        delete_job(j_id)  # Delete files and memory
