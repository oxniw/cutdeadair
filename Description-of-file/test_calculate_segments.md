# Description: test_calculate_segments.py

## Overview
Automated unit test suite verifying the pure mathematical domain logic for interval calculation, overlapping silence merging, boundary clamping, margin buffer expansion, and pause duration shortening.

## Exports & Functions
- `class TestCalculateSegments(unittest.TestCase)`
  - `test_no_silence_keeps_whole_file()`: Verifies full duration is retained when zero silence exists.
  - `test_single_silence_cut_mode()`: Verifies middle dead air excision with margin buffers.
  - `test_shorten_mode_target_pause()`: Verifies that natural shortening leaves precisely the target pause length.
  - `test_merge_overlapping_silences()`: Verifies proper consolidation of abutting and intersecting silence intervals.
  - `test_silence_at_audio_edges()`: Verifies leading and trailing dead air trimming at audio boundaries.

## Dependencies & Data Flow
- **Imports**: `unittest`, `domain_models.SilenceInterval`, `domain_models.KeepSegment`, `domain_models.ProcessingSettings`, `calculate_segments.calculate_segments`, `calculate_segments.merge_overlapping_intervals`.
- **Invoked By**: `python test_calculate_segments.py` or test runners.
- **Data Flow**: Supplies mock numeric intervals -> tests pure functions in memory -> asserts expected interval boundaries without file I/O.
