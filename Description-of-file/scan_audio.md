# Description: scan_audio.py

## Overview
Non-destructive pre-flight analyzer that queries audio/video duration, detects dead air intervals, measures sound power levels, detects video streams, and calculates kept segments to provide live preview statistics without altering media on disk.

## Exports & Functions
- `scan_audio(file_path: str, settings: ProcessingSettings) -> AudioScanResult`
  - **Description**: Inspects an audio or video file and computes silence duration, speech segments, sound power metrics, video presence, estimated new length, and time savings percentage.
  - **Parameters**:
    - `file_path`: Path to the media file.
    - `settings`: Configured threshold, min duration, and padding settings.
  - **Returns**: `AudioScanResult` detailing all pre-flight metrics including `is_video`.

## Dependencies & Data Flow
- **Imports**: `domain_models.*`, `detect_silence.get_audio_duration`, `detect_silence.detect_silence`, `detect_silence.measure_audio_volume`, `detect_silence.is_video_file`, `calculate_segments.calculate_segments`.
- **Invoked By**: `gui_components.py`, `process_audio_file.py`.
- **Data Flow**: `file_path` -> duration probe -> volume measurement -> video stream detection -> silence detection -> segment calculation -> returns `AudioScanResult`.
