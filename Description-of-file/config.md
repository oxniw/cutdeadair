# Description: config.py

## Overview
Central application configuration module containing default audio parameters, supported file formats, preset profiles, and UI window styling constants.

## Exports & Functions
- `SUPPORTED_EXTENSIONS: Tuple[str, ...]`
  - Tuple of supported audio file suffixes (`.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`, `.ogg`, `.wma`, `.aiff`).
- `DEFAULT_SOUND_POWER_THRESHOLD_DB: float`
  - Default decibel cutoff below full scale (-32.0 dBFS); audio power <= this is cut.
- `DEFAULT_SILENCE_THRESHOLD_DB: float`
  - Backward-compatible alias for sound power threshold.
- `SOUND_POWER_MIN_DB: float`, `SOUND_POWER_MAX_DB: float`
  - Slider boundaries for sound power cutoff (-70.0 dB to -5.0 dB).
- `ZONE_DURATION_MIN_S: float`, `ZONE_DURATION_MAX_S: float`
  - Slider boundaries for low-power zone duration (0.05s to 3.0s).
- `DEFAULT_MIN_SILENCE_DURATION: float`
  - Minimum length of low-power duration in seconds to trigger cutting (0.6s).
- `DEFAULT_MARGIN_PADDING: float`
  - Default safety buffer in seconds placed around spoken audio (0.15s).
- `DEFAULT_TARGET_PAUSE: float`
  - Default duration in seconds to shorten pauses to in natural shortening mode (0.3s).
- `DEFAULT_CUT_MODE: str`
  - Default dead air mode ("shorten").
- `DEFAULT_OUTPUT_SUFFIX: str`
  - Filename suffix appended to processed files (`"_cut"`).
- `DEFAULT_OUTPUT_SUBFOLDER: str`
  - Name of the default subfolder created for exports (`"processed"`).
- `PRESETS: Dict[str, Dict[str, Any]]`
  - Pre-packaged parameter profiles ("Podcast / Voiceover", "Aggressive Cut", "Subtle Breath Retain").
- `APP_TITLE`, `APP_WINDOW_SIZE`, `APP_MIN_SIZE`
  - Desktop GUI configuration settings.

## Dependencies & Data Flow
- **Imports**: `typing.Dict`, `typing.Any`, `typing.Tuple`.
- **Invoked By**: `gui_components.py`, `process_audio_file.py`.
- **Data Flow**: Provides static constants and configuration structures to the GUI and audio processing pipeline.
