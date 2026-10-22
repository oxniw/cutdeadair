# Description: render_audio.py

## Overview
Audio rendering engine applying FFmpeg aselect and asetpts filtergraphs to splice keep intervals into seamless output audio.

## Exports & Functions
- `render_audio(input_path: str, output_path: str, keep_segments: List[KeepSegment], progress_callback: Optional[Callable[[float, str], None]] = None) -> str`
  - **Description**: Slices sound segments and writes clean output audio file.
  - **Parameters**: `input_path`, `output_path`, `keep_segments`, `progress_callback`.
  - **Returns**: Path to processed output file.

## Dependencies & Data Flow
- **Imports**: `os`, `subprocess`, `domain_models.KeepSegment`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Source audio + keep segments -> FFmpeg aselect filtergraph -> generated audio file.
