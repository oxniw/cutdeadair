# Description: config.py

## Overview
Web application configuration constants defining dynamic network settings from environment variables, storage locations, upload size limits, supported media formats, presets, and slider bounds.

## Exports & Functions
- `SERVER_HOST: str`, `SERVER_PORT: int`: Server binding address loaded from `HOST` and `PORT` environment variables (default `0.0.0.0:8080`).
- `CORS_ALLOWED_ORIGINS: str`: Allowed cross-origin source string loaded from `CORS_ALLOWED_ORIGINS` (default `*`).
- `MAX_UPLOAD_SIZE_BYTES: int`: Maximum upload payload size (500 MB).
- `JOB_EXPIRATION_SECONDS: int`: Cache lifetime for uploaded files (1 hour).
- `TEMP_UPLOAD_DIR: str`, `TEMP_PROCESSED_DIR: str`: Isolated filesystem directories.
- `SUPPORTED_AUDIO_EXTENSIONS: Tuple[str, ...]`, `SUPPORTED_VIDEO_EXTENSIONS: Tuple[str, ...]`: Whitelisted formats.
- `DEFAULT_SOUND_POWER_THRESHOLD_DB: float`: Default sound power cutoff (-32.0 dB).
- `SOUND_POWER_MIN_DB: float`, `SOUND_POWER_MAX_DB: float`: Sound power slider boundaries.
- `PRESETS: Dict[str, Dict[str, Any]]`: Preconfigured parameter profiles.

## Dependencies & Data Flow
- **Imports**: `os`, `typing.Dict`, `typing.Any`, `typing.Tuple`.
- **Invoked By**: `server_router.py`, `main.py`.
- **Data Flow**: Supplies static and environment parameters to routing, validation, and storage components.
