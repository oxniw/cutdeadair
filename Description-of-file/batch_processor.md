# Description: batch_processor.py

## Overview
Coordinates multi-file queue processing, distributing individual file jobs, broadcasting progress updates, supporting mid-batch user cancellation, and collecting execution summaries.

## Exports & Functions
- `process_batch(files: List[str], settings: ProcessingSettings, on_file_start: Optional[Callable[[int, int, str], None]] = None, on_file_progress: Optional[Callable[[int, int, float, str], None]] = None, on_file_complete: Optional[Callable[[int, int, ProcessSummary], None]] = None, is_cancelled: Optional[Callable[[], bool]] = None) -> List[ProcessSummary]`
  - **Description**: Iterates through the provided list of files, invokes `process_audio_file` on each, respects cancellation, and emits progress metrics.
  - **Parameters**:
    - `files`: Queue of audio file paths.
    - `settings`: Configured audio processing parameters.
    - `on_file_start`: Callback invoked when starting a file.
    - `on_file_progress`: Callback updating percentage and sub-step.
    - `on_file_complete`: Callback invoked when a file finishes.
    - `is_cancelled`: Check callback returning True if user pressed Cancel.
  - **Returns**: List of `ProcessSummary` results.

## Dependencies & Data Flow
- **Imports**: `typing.List`, `typing.Callable`, `typing.Optional`, `domain_models.ProcessingSettings`, `domain_models.ProcessSummary`, `process_audio_file.process_audio_file`.
- **Invoked By**: `gui_components.py`.
- **Data Flow**: Queue of paths -> sequential dispatch to `process_audio_file` with cancellation check -> emits UI progress events -> aggregates results list.
