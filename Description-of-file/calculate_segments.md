# Description: calculate_segments.py

## Overview
Pure algorithmic domain module providing mathematical calculation of audio segments to keep, interval merging, boundary clamping, safety margin padding, and pause duration shortening.

## Exports & Functions
- `merge_overlapping_intervals(intervals: List[SilenceInterval]) -> List[SilenceInterval]`
  - **Description**: Merges adjacent or overlapping silence intervals into sorted, continuous spans.
  - **Parameters**:
    - `intervals`: Raw list of silence intervals.
  - **Returns**: Consolidated list of non-overlapping intervals.

- `calculate_segments(total_duration: float, silence_intervals: List[SilenceInterval], settings: ProcessingSettings) -> List[KeepSegment]`
  - **Description**: Computes the exact spans of sound to retain based on identified dead air, margin padding, and target pause durations.
  - **Parameters**:
    - `total_duration`: Audio duration in seconds.
    - `silence_intervals`: Detected silence blocks.
    - `settings`: ProcessingSettings specifying mode ("cut" vs "shorten"), margin, and target pause.
  - **Returns**: List of non-overlapping `KeepSegment` instances ready for audio rendering.

## Dependencies & Data Flow
- **Imports**: `domain_models.SilenceInterval`, `domain_models.KeepSegment`, `domain_models.ProcessingSettings`.
- **Invoked By**: `scan_audio.py`, `test_calculate_segments.py`.
- **Data Flow**: Consumes raw detected silence intervals -> derives speech intervals -> applies padding/pause shortening rules -> produces sliced keep segments. Operates in pure memory with no file I/O.
