# ==============================================================================
# File: .//Description-of-file/config.md
# Overview: Web application configuration defining network ports, upload limits, media extensions, and audio presets.
# ==============================================================================

import os
from typing import Dict, Any, Tuple

# Server network settings
SERVER_HOST: str = os.getenv("HOST", "0.0.0.0")  # Bind address from environment
SERVER_PORT: int = int(os.getenv("PORT", "8080"))  # Listening port from environment
CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "*")  # Allowed CORS origins

# Security and storage limits
MAX_UPLOAD_SIZE_BYTES: int = 500 * 1024 * 1024  # 500 MB max file size
JOB_EXPIRATION_SECONDS: int = 3600               # 1 hour job lifetime
TEMP_UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "uploads")
TEMP_PROCESSED_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "processed")
TEMP_JOBS_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "jobs")

# Supported media extensions
SUPPORTED_AUDIO_EXTENSIONS: Tuple[str, ...] = (
    ".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma", ".aiff"
)
SUPPORTED_VIDEO_EXTENSIONS: Tuple[str, ...] = (
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v", ".ts"
)
SUPPORTED_EXTENSIONS: Tuple[str, ...] = SUPPORTED_AUDIO_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS

# Audio detection defaults
DEFAULT_SOUND_POWER_THRESHOLD_DB: float = -32.0
DEFAULT_MIN_SILENCE_DURATION: float = 0.6
DEFAULT_MARGIN_PADDING: float = 0.15
DEFAULT_TARGET_PAUSE: float = 0.3
DEFAULT_CUT_MODE: str = "shorten"
DEFAULT_OUTPUT_SUFFIX: str = "_cut"

# Sliders boundaries
SOUND_POWER_MIN_DB: float = -70.0
SOUND_POWER_MAX_DB: float = -5.0
ZONE_DURATION_MIN_S: float = 0.05
ZONE_DURATION_MAX_S: float = 3.0

# Video defaults
DEFAULT_VIDEO_PRESET: str = "fast"
DEFAULT_VIDEO_CRF: int = 22

# Presets
PRESETS: Dict[str, Dict[str, Any]] = {
    "Podcast / Voiceover": {
        "description": "Natural speech cadence, keeps breaths, shortens pauses to 0.3s.",
        "silence_threshold_db": -32.0,
        "min_silence_duration": 0.6,
        "margin_padding": 0.15,
        "target_pause": 0.3,
        "mode": "shorten",
    },
    "Aggressive Cut": {
        "description": "Fast video editing, cuts silence completely with tight padding.",
        "silence_threshold_db": -28.0,
        "min_silence_duration": 0.4,
        "margin_padding": 0.08,
        "target_pause": 0.15,
        "mode": "cut",
    },
    "Subtle Breath Retain": {
        "description": "Gentle narration trimming for audiobooks, preserving pace.",
        "silence_threshold_db": -38.0,
        "min_silence_duration": 1.0,
        "margin_padding": 0.25,
        "target_pause": 0.45,
        "mode": "shorten",
    },
}
