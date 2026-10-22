# Description: process_audio_file.py

## Overview
High-level media orchestrator that resolves safe output file paths (preserving video containers or switching to .mp3 for audio extraction), executes pre-flight analysis, routes to `render_video` or `render_audio`, and returns a `ProcessSummary`.

## Exports & Functions
- `build_output_path(input_path: str, settings: ProcessingSettings, is_video: bool = False) -> str`
  - **Description**: Generates the target output path using the specified output folder and suffix, adjusting extension to `.mp3` if extracting audio from video.
  - **Parameters**:
    - `input_path`: Original media path.
    - `settings`: Processing settings containing output directory and suffix.
    - `is_video`: True if input media contains a video stream.
  - **Returns**: Target output file path.

- `process_audio_file(file_path: str, settings: ProcessingSettings, scan_result: Optional[AudioScanResult] = None, progress_callback: Optional[Callable[[float, str], None]] = None) -> ProcessSummary`
  - **Description**: Runs full end-to-end processing for a single audio or video file, dispatching to `render_video` when video streams are present.
  - **Parameters**:
    - `file_path`: Path to audio or video file.
    - `settings`: Processing parameters (including video mode and CRF quality).
    - `scan_result`: Optional pre-computed scan to skip redundant analysis.
    - `progress_callback`: Progress feedback callback.
  - **Returns**: `ProcessSummary` with success state, original/new durations, video flag, and time saved.

## Dependencies & Data Flow
- **Imports**: `os`, `typing.Callable`, `typing.Optional`, `config.*`, `domain_models.*`, `scan_audio.scan_audio`, `render_audio.render_audio`, `render_video.render_video`, `detect_silence.get_audio_duration`.
- **Invoked By**: `batch_processor.py`.
- **Data Flow**: Media file -> scan -> routes to `render_video` or `render_audio` -> measures duration -> returns `ProcessSummary`.
