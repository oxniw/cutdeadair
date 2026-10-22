# Description: test_web_app.py

## Overview
Automated test suite verifying security validation (path traversal sanitization, extension checks, payload size bounds) and pure domain interval math.

## Exports & Functions
- `class TestWebAppSecurityAndDomain(unittest.TestCase)`
  - `test_sanitize_filename_traversal`: Verifies elimination of path traversal sequences.
  - `test_validate_file_extension`: Asserts file extension whitelist enforcement.
  - `test_validate_file_size`: Confirms payload size boundaries.
  - `test_generate_job_id`: Checks 32-character random hex token format.
  - `test_calculate_segments_silence_cut`: Tests silence excision and margin padding.

## Dependencies & Data Flow
- **Imports**: `unittest`, `security.*`, `domain_models.*`, `calculate_segments.*`.
- **Invoked By**: `python test_web_app.py`.
- **Data Flow**: Test fixtures -> security sanitization / interval math -> assertions.
