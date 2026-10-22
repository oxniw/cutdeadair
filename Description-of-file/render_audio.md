# Description: render_audio.py

## Overview
Audio rendering engine utilizing an FFmpeg `filter_complex_script` pipeline with `atrim` and `concat` filters to slice out dead air and output seamless audio files without command-length constraints.

## Exports & Functions
- `render_audio(input_path: str, output_path: str, keep_segments: List[KeepSegment], progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Generates a temporary filter complex script defining the trim boundaries for all keep segments, passes it to FFmpeg, and writes the spliced audio file.
  - **Parameters**:
    - `input_path`: Path to original audio file.
    - `output_path`: Target destination file path.
    - `keep_segments`: List of `KeepSegment` spans to splice together.
    - `progress_callback`: Optional callback taking `(fraction, message)` for live UI feedback.
  - **Returns**: Absolute path to the completed rendered audio file.

## Dependencies & Data Flow
- **Imports**: `os`, `shutil`, `subprocess`, `tempfile`, `typing.List`, `typing.Callable`, `typing.Optional`, `domain_models.KeepSegment`.
- **Invoked By**: `process_audio_file.py`.
- **Data Flow**: Takes `keep_segments` -> writes `temp_filter_script.txt` -> invokes FFmpeg subprocess -> outputs rendered audio to destination path -> cleans up temporary script.
