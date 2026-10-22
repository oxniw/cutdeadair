# Description: job_manager.py

## Overview
Thread-safe and disk-persistent state store tracking upload sessions, progress updates, and file cleanup with resilience against container crashes and cloud restarts.

## Exports & Functions
- `create_job(filename: str, upload_path: str) -> str`: Allocates a new job entry, persists metadata to disk as JSON, and registers in-memory cache.
- `get_job(job_id: str) -> Optional[Dict[str, Any]]`: Retrieves current job data from memory or recovers from disk JSON. Automatically transitions interrupted jobs to failed state.
- `update_job(job_id: str, **kwargs) -> None`: Updates job fields safely in memory and commits changes to disk JSON.
- `delete_job(job_id: str) -> None`: Removes job record from memory and disk, and purges uploaded and rendered media files.
- `cleanup_expired_jobs(max_age_seconds: int) -> None`: Purges old jobs and temporary files based on epoch timestamps.

## Dependencies & Data Flow
- **Imports**: `os`, `time`, `json`, `threading`, `dataclasses`, `config.TEMP_JOBS_DIR`, `security.*`.
- **Invoked By**: `server_router.py`.
- **Data Flow**: Tracks state between client polling and background rendering threads across container restarts.
