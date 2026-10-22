# Description: render_video.py

## Overview
High-performance video rendering engine that synchronizes video frame trimming and audio cutting using FFmpeg `trim`, `atrim`, and `concat` filtergraphs, with automated chunking for long recordings.

## Exports & Functions
- `_render_video_single_chunk(input_path: str, output_path: str, segments: List[KeepSegment], video_preset: str, video_crf: int) -> None`
  - **Description**: Slices and concatenates a batch of video/audio segments in a single FFmpeg invocation.
  - **Parameters**:
    - `input_path`: Path to source video file.
    - `output_path`: Path to output file or chunk.
    - `segments`: KeepSegment objects to include.
    - `video_preset`: Encoding speed preset (e.g. "fast").
    - `video_crf`: Quality factor (default 22).

- `render_video(input_path: str, output_path: str, keep_segments: List[KeepSegment], video_preset: str = "fast", video_crf: int = 22, progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Public entry point for rendering trimmed video with synchronized audio. Automatically divides large segment lists into manageable chunks and merges them via stream-copy concat.
  - **Parameters**:
    - `input_path`: Original video path.
    - `output_path`: Destination video path.
    - `keep_segments`: Sliced speech intervals to retain.
    - `video_preset`: H.264 preset.
    - `video_crf`: Video quality setting.
    - `progress_callback`: Progress feedback reporter.
  - **Returns**: Absolute path to the finalized video file.

## Dependencies & Data Flow
- **Imports**: `os`, `subprocess`, `tempfile`, `typing.List`, `typing.Callable`, `typing.Optional`, `domain_models.KeepSegment`.
- **Invoked By**: `process_audio_file.py`.
- **Data Flow**: Source video + `keep_segments` -> generates filtergraph -> encodes with H.264/AAC -> outputs synchronized video file without A/V drift.
