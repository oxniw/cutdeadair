# Description: render_video.py

## Overview
Low-memory sequential video rendering engine slicing segments individually and stitching via concat demuxer to eliminate Out-Of-Memory (OOM) crashes in constrained container environments (e.g. Render Free Tier 512 MB RAM).

## Exports & Functions
- `_render_single_slice(input_path: str, output_path: str, start: float, end: float, video_preset: str = "ultrafast", video_crf: int = 22) -> None`
  - **Description**: Renders one isolated video slice with single-thread encoding and zero lookahead buffers to bound memory usage below 40 MB.
- `render_video(input_path: str, output_path: str, keep_segments: List[KeepSegment], video_preset: str = "ultrafast", video_crf: int = 22, progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Slices video and audio synchronously, renders parts sequentially, and stitches them instantly using FFmpeg concat demuxer without re-encoding.
  - **Returns**: Path to final rendered video.

## Dependencies & Data Flow
- **Imports**: `os`, `subprocess`, `tempfile`, `domain_models.KeepSegment`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Source video -> sequential slice extraction -> concat demuxer stream copy -> final media.
