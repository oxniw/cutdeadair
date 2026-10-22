# Description: domain_models.py

## Overview
Pure domain data models and dataclasses defining silence intervals, keep segments, pre-flight scan results, execution settings, and rendering summaries.

## Exports & Functions
- `class SilenceInterval`
  - **Description**: Immutable dataclass representing a continuous dead air window.
  - **Properties**:
    - `start: float`: Starting timestamp in seconds.
    - `end: float`: Ending timestamp in seconds.
    - `duration: float`: Computed duration in seconds (`end - start`).
- `class KeepSegment`
  - **Description**: Immutable dataclass defining an audio segment retained for rendering.
  - **Properties**:
    - `start: float`: Audio segment start timestamp in seconds.
    - `end: float`: Audio segment end timestamp in seconds.
    - `duration: float`: Segment duration in seconds.
- `class ProcessingSettings`
  - **Description**: Configurable settings passed to silence detectors and segment calculators.
  - **Fields**: `threshold_db`, `min_silence_duration`, `margin_padding`, `target_pause`, `mode`, `output_dir`, `output_suffix`.
- `class AudioScanResult`
  - **Description**: Pre-flight inspection metrics before rendering.
  - **Properties**: `file_path`, `total_duration`, `silence_intervals`, `keep_segments`, `mean_power_db`, `max_power_db`, `total_silence_duration`, `estimated_output_duration`, `time_saved`, `percentage_saved`.
- `class ProcessSummary`
  - **Description**: Execution outcome of an audio render.
  - **Properties**: `file_path`, `output_path`, `success`, `error_message`, `original_duration`, `processed_duration`, `time_saved`.

## Dependencies & Data Flow
- **Imports**: `dataclasses.dataclass`, `dataclasses.field`, `typing.List`, `typing.Optional`.
- **Invoked By**: `calculate_segments.py`, `detect_silence.py`, `render_audio.py`, `scan_audio.py`, `process_audio_file.py`, `batch_processor.py`, `gui_components.py`, `test_calculate_segments.py`.
- **Data Flow**: Carries typed data structures throughout the application without coupling components to external libraries or I/O.
