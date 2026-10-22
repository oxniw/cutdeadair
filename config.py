# ==============================================================================
# File: .//Description-of-file/config.md
# Overview: Central application configuration, presets, default parameters, and supported audio extensions.
# ==============================================================================

from typing import Dict, Any, Tuple

# Supported audio file extensions
SUPPORTED_AUDIO_EXTENSIONS: Tuple[str, ...] = (
    ".mp3",
    ".wav",
    ".flac",
    ".aac",
    ".m4a",
    ".ogg",
    ".wma",
    ".aiff",
)

# Supported video file extensions for Video Mode
SUPPORTED_VIDEO_EXTENSIONS: Tuple[str, ...] = (
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
    ".ts",
)

# Combined supported media extensions
SUPPORTED_EXTENSIONS: Tuple[str, ...] = SUPPORTED_AUDIO_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS

# Default parameter values
DEFAULT_SOUND_POWER_THRESHOLD_DB: float = -32.0  # Decibels below full scale (dBFS); sound power <= this is cut
DEFAULT_SILENCE_THRESHOLD_DB: float = DEFAULT_SOUND_POWER_THRESHOLD_DB  # Backward-compatible alias
DEFAULT_MIN_SILENCE_DURATION: float = 0.6       # Minimum duration in seconds of low power to cut
DEFAULT_MARGIN_PADDING: float = 0.15            # Lead-in/lead-out buffer in seconds to keep around speech
DEFAULT_TARGET_PAUSE: float = 0.3               # Target duration in seconds when shortening pauses
DEFAULT_CUT_MODE: str = "shorten"               # "cut" (strip completely) or "shorten" (reduce to target pause)
DEFAULT_OUTPUT_SUFFIX: str = "_cut"             # Suffix appended before the file extension
DEFAULT_OUTPUT_SUBFOLDER: str = "processed"     # Default output subfolder name

# Slider boundary constants
SOUND_POWER_MIN_DB: float = -70.0               # Minimum slider sound power in dB
SOUND_POWER_MAX_DB: float = -5.0                # Maximum slider sound power in dB
ZONE_DURATION_MIN_S: float = 0.05               # Minimum slider low-power zone duration
ZONE_DURATION_MAX_S: float = 3.0                # Maximum slider low-power zone duration

# Preset configurations
PRESETS: Dict[str, Dict[str, Any]] = {
    "Podcast / Voiceover": {
        "description": "Natural sounding speech, retains subtle breaths, shortens pauses to 0.3s.",
        "silence_threshold_db": -32.0,
        "min_silence_duration": 0.6,
        "margin_padding": 0.15,
        "target_pause": 0.3,
        "mode": "shorten",
    },
    "Aggressive Cut": {
        "description": "Fast-paced content / YouTube editing, cuts dead air completely with tight padding.",
        "silence_threshold_db": -28.0,
        "min_silence_duration": 0.4,
        "margin_padding": 0.08,
        "target_pause": 0.15,
        "mode": "cut",
    },
    "Subtle Breath Retain": {
        "description": "Gentle trimming for audiobooks or delicate narration, preserving natural cadence.",
        "silence_threshold_db": -38.0,
        "min_silence_duration": 1.0,
        "margin_padding": 0.25,
        "target_pause": 0.45,
        "mode": "shorten",
    },
}

# Video Mode default rendering settings
DEFAULT_VIDEO_PRESET: str = "fast"               # ffmpeg libx264 preset (ultrafast, superfast, veryfast, faster, fast, medium)
DEFAULT_VIDEO_CRF: int = 22                      # Constant Rate Factor (0-51, lower = higher quality, 18-24 optimal)
DEFAULT_EXPORT_AUDIO_ONLY: bool = False          # False = keep full video synced; True = extract audio only

# UI Application styling configuration
APP_TITLE: str = "Dead Air Cutter (Audio & Video)"
APP_WINDOW_SIZE: str = "980x740"
APP_MIN_SIZE: Tuple[int, int] = (840, 620)
