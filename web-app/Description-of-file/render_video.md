# Description: render_video.py

## Overview
Synchronized video and audio rendering engine using FFmpeg trim, atrim, and concat filters with chunking support for long files.

## Exports & Functions
- `_render_video_single_chunk(input_path: str, output_path: str, segments: List[KeepSegment], video_preset: str, video_crf: int) -> None`
  - **Description**: Slices and concatenates video and audio segments in a single pass.
- `render_video(input_path: str, output_path: str, keep_segments: List[KeepSegment], video_preset: str, video_crf: int, progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Trims video frames and audio in exact lockstep, automatically handling large segment lists.
  - **Returns**: Path to final processed video.

## Dependencies & Data Flow
- **Imports**: `os`, `subprocess`, `tempfile`, `domain_models.KeepSegment`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Source video + keep segments -> trim/atrim filtergraph -> rendered synchronized video.
