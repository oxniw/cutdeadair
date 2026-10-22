# Description: job_manager.py

## Overview
In-memory thread-safe state store tracking upload sessions, progress updates, and file cleanup.

## Exports & Functions
- `create_job(filename: str, upload_path: str) -> str`: Allocates a new job entry.
- `get_job(job_id: str) -> Optional[Dict[str, Any]]`: Retrieves current job data.
- `update_job(job_id: str, **kwargs) -> None`: Updates job fields safely.
- `delete_job(job_id: str) -> None`: Removes job record and deletes associated disk files.
- `cleanup_expired_jobs(max_age_seconds: int) -> None`: Purges old jobs and temporary files.

## Dependencies & Data Flow
- **Imports**: `os`, `time`, `threading`, `security.generate_secure_job_id`.
- **Invoked By**: `server_router.py`.
- **Data Flow**: Tracks state between client polling and background rendering threads.
