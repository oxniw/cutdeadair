# Description: detect_silence.py

## Overview
Adapter calling FFprobe and FFmpeg silencedetect to measure media durations, silence intervals, sound power levels, and video streams.

## Exports & Functions
- `get_audio_duration(file_path: str) -> float`: Probes media duration with FFprobe.
- `detect_silence(file_path: str, threshold_db: float, min_silence_duration: float, total_duration: float) -> List[SilenceInterval]`: Detects low power dead air intervals.
- `measure_audio_volume(file_path: str) -> Tuple[float | None, float | None]`: Measures mean and peak volume in dBFS.
- `is_video_file(file_path: str) -> bool`: Checks if file contains a video stream.

## Dependencies & Data Flow
- **Imports**: `re`, `subprocess`, `domain_models.SilenceInterval`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Media file -> executes FFprobe/FFmpeg subprocesses with array arguments -> parses log lines -> returns structured metrics.
