# Description: security.py

## Overview
Defensive security utilities preventing path traversal attacks, validating upload extensions and file sizes, issuing cryptographically secure job IDs, and providing security response headers including CORS controls.

## Exports & Functions
- `sanitize_filename(filename: str) -> str`
  - **Description**: Strips path separators, null bytes, and non-whitelisted characters to prevent directory traversal.
  - **Parameters**: `filename: str`
  - **Returns**: Clean safe basename.
- `validate_file_extension(filename: str, allowed_extensions: Tuple[str, ...]) -> bool`
  - **Description**: Verifies file extension against the whitelist.
  - **Parameters**: `filename: str`, `allowed_extensions: Tuple[str, ...]`.
  - **Returns**: True if valid, False otherwise.
- `validate_file_size(size: int, max_bytes: int) -> bool`
  - **Description**: Verifies upload size is within the allowed bounds.
  - **Parameters**: `size: int`, `max_bytes: int`.
  - **Returns**: True if within limits.
- `generate_secure_job_id() -> str`
  - **Description**: Generates a 128-bit random hex token using `secrets`.
  - **Returns**: Cryptographic hex string.
- `get_security_headers(allowed_origin: str = "*") -> Dict[str, str]`
  - **Description**: Returns defensive HTTP headers (`X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`, and CORS headers).
  - **Parameters**: `allowed_origin: str`
  - **Returns**: Dictionary of header name/value pairs.

## Dependencies & Data Flow
- **Imports**: `os`, `re`, `secrets`, `typing.Tuple`, `typing.Dict`.
- **Invoked By**: `server_router.py`, `job_manager.py`.
- **Data Flow**: Untrusted incoming requests -> sanitization and validation -> safe internal representation.
