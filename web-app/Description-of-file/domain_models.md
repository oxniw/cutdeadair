# Description: domain_models.py

## Overview
Domain dataclasses encapsulating silence intervals, keep segments, processing settings, scan metrics, and rendering summaries.

## Exports & Functions
- `class SilenceInterval`: Dataclass tracking silence start, end, and duration.
- `class KeepSegment`: Dataclass tracking retained speech interval boundaries.
- `class ProcessingSettings`: Dataclass holding threshold, padding, mode, and video parameters.
- `class MediaScanResult`: Dataclass storing pre-flight metrics, duration, power levels, and estimated savings.
- `class ProcessSummary`: Dataclass containing execution result, final duration, and output file path.

## Dependencies & Data Flow
- **Imports**: `dataclasses.dataclass`, `dataclasses.field`, `typing.List`, `typing.Optional`.
- **Invoked By**: `calculate_segments.py`, `detect_silence.py`, `render_audio.py`, `render_video.py`, `process_media.py`, `server_router.py`.
- **Data Flow**: Carries typed data structures throughout the web application pipeline.
