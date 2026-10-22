# Description: render_video.py

## Overview
Memory-budgeted concurrent video rendering engine dynamically adjusting workers and threads to available RAM without exceeding container memory limits.

## Exports & Functions
- `_render_single_slice(input_path: str, output_path: str, start: float, end: float, video_preset: str = "ultrafast", video_crf: int = 22, threads: int = 1) -> None`
  - **Description**: Renders one isolated video slice with bounded thread count and zero lookahead buffers to limit memory usage per worker.
- `render_video(input_path: str, output_path: str, keep_segments: List[KeepSegment], video_preset: str = "ultrafast", video_crf: int = 22, progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Calculates available memory budget via `system_resources.py`, executes slice rendering using an optimal concurrent worker pool, and stitches finished slices via FFmpeg concat demuxer without re-encoding.
  - **Returns**: Path to final rendered video.

## Dependencies & Data Flow
- **Imports**: `os`, `subprocess`, `tempfile`, `concurrent.futures`, `domain_models.KeepSegment`, `system_resources.calculate_render_budget`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Source video -> dynamic resource budget -> concurrent slice rendering -> concat demuxer stream copy -> final media.
