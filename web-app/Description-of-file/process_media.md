# Description: process_media.py

## Overview
Media pipeline coordinator managing pre-flight scanning, path resolution, and dispatching to video or audio renderers.

## Exports & Functions
- `scan_media(file_path: str, settings: ProcessingSettings) -> MediaScanResult`
  - **Description**: Performs non-destructive silence detection, power level measurements, and time savings calculations.
- `process_media(file_path: str, output_path: str, settings: ProcessingSettings, scan_result: Optional[MediaScanResult] = None, progress_callback: Optional[Callable[[float, str], None]] = None) -> ProcessSummary`
  - **Description**: Renders cut media to the target destination, choosing between video and audio engines.

## Dependencies & Data Flow
- **Imports**: `os`, `domain_models.*`, `calculate_segments.*`, `detect_silence.*`, `render_audio.*`, `render_video.*`.
- **Invoked By**: `server_router.py`.
- **Data Flow**: Job media file -> scan/process -> output file path -> returns summary.
