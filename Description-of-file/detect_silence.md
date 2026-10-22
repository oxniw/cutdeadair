# Description: detect_silence.py

## Overview
Audio analysis adapter interface executing FFprobe to measure audio length and FFmpeg `silencedetect` audio filter to discover exact dead air timestamps.

## Exports & Functions
- `get_audio_duration(file_path: str) -> float`
  - **Description**: Probes an audio file using FFprobe to extract total duration in seconds.
  - **Parameters**:
    - `file_path`: Path to the media file.
  - **Returns**: Duration in seconds as a float.

- `detect_silence(file_path: str, threshold_db: float, min_silence_duration: float, total_duration: float) -> List[SilenceInterval]`
  - **Description**: Spawns FFmpeg with the `silencedetect` audio filter and parses stdout/stderr log lines for silence boundaries.
  - **Parameters**:
    - `file_path`: Input audio file path.
    - `threshold_db`: Noise floor cutoff in dB (e.g., -32.0).
    - `min_silence_duration`: Minimum silence length to detect (e.g., 0.6).
    - `total_duration`: Total file length for trailing silence boundary clamping.
- `measure_audio_volume(file_path: str) -> Tuple[float | None, float | None]`
  - **Description**: Probes audio file with FFmpeg `volumedetect` filter to measure mean sound power and peak sound power in dBFS.
  - **Parameters**:
    - `file_path`: Path to the media file.
  - **Returns**: Tuple of `(mean_power_db, max_power_db)` or `(None, None)` on failure.

- `is_video_file(file_path: str) -> bool`
  - **Description**: Inspects media container via FFprobe to verify if a video stream (`v:0`) exists.
  - **Parameters**:
    - `file_path`: Media file path.
  - **Returns**: True if file contains a video stream, False otherwise.

## Dependencies & Data Flow
- **Imports**: `re`, `subprocess`, `typing.Tuple`, `typing.List`, `domain_models.SilenceInterval`.
- **Invoked By**: `scan_audio.py`, `process_audio_file.py`.
- **Data Flow**: Reads audio media through FFmpeg subprocess -> parses regex matches (`silence_start`, `silence_end`, `mean_volume`, `max_volume`) -> returns structured `SilenceInterval` list and power levels.
