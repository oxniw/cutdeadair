# Description: calculate_segments.py

## Overview
Pure algorithmic interval calculations for silence merging, speech extraction, boundary clamping, safety margins, and pause duration shortening.

## Exports & Functions
- `merge_overlapping_intervals(intervals: List[SilenceInterval]) -> List[SilenceInterval]`
  - **Description**: Consolidates overlapping or adjacent silence intervals into unified spans.
  - **Parameters**: `intervals: List[SilenceInterval]`.
  - **Returns**: Consolidated list of non-overlapping intervals.
- `calculate_segments(total_duration: float, silence_intervals: List[SilenceInterval], settings: ProcessingSettings) -> List[KeepSegment]`
  - **Description**: Computes keep intervals based on silence detections, margin buffers, and target pause durations.
  - **Parameters**: `total_duration: float`, `silence_intervals: List[SilenceInterval]`, `settings: ProcessingSettings`.
  - **Returns**: List of `KeepSegment` instances ready for rendering.

## Dependencies & Data Flow
- **Imports**: `domain_models.SilenceInterval`, `domain_models.KeepSegment`, `domain_models.ProcessingSettings`.
- **Invoked By**: `process_media.py`.
- **Data Flow**: Silence intervals + duration -> mathematical transformation -> keep segment list. Operates in pure memory.
