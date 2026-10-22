# ==============================================================================
# File: .//Description-of-file/security.md
# Overview: Security validation routines preventing path traversal, restricting upload sizes, and setting defensive HTTP headers.
# ==============================================================================

import os
import re
import secrets
from typing import Tuple, Dict


def sanitize_filename(filename: str) -> str:
    """
    Strips directory separators, null bytes, and non-whitelisted characters.
    Prevents path traversal attacks like ../ or absolute file paths.
    """
    # Keep only the basename
    base = os.path.basename(filename).strip()
    # Remove null bytes
    base = base.replace("\x00", "")
    # Keep alphanumeric characters, underscores, dashes, and single dots
    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
    # Prevent hidden files or leading dots
    safe_name = safe_name.lstrip(".")
    if not safe_name:
        safe_name = f"upload_{secrets.token_hex(4)}"
    return safe_name


def validate_file_extension(filename: str, allowed_extensions: Tuple[str, ...]) -> bool:
    """Verifies that the file extension exists in the allowed whitelist."""
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_extensions


def validate_file_size(size: int, max_bytes: int) -> bool:
    """Ensures uploaded payload size does not exceed the allowed threshold."""
    return 0 < size <= max_bytes


def generate_secure_job_id() -> str:
    """Generates an unguessable 128-bit cryptographic hex identifier for upload sessions."""
    return secrets.token_hex(16)


def get_security_headers(allowed_origin: str = "*") -> Dict[str, str]:
    """Returns defensive security headers to mitigate XSS, framing, MIME sniffing, and cross-origin issues."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self' 'unsafe-inline' data:; media-src 'self' blob:; connect-src 'self' *;",
        "Referrer-Policy": "no-referrer",
        "Access-Control-Allow-Origin": allowed_origin,
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Filename",
    }
