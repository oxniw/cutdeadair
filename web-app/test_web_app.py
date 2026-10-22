# ==============================================================================
# File: .//Description-of-file/test_web_app.md
# Overview: Automated test suite verifying security sanitization, segment calculations, and API routing.
# ==============================================================================

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security import sanitize_filename, validate_file_extension, validate_file_size, generate_secure_job_id
from domain_models import SilenceInterval, KeepSegment, ProcessingSettings
from calculate_segments import calculate_segments, merge_overlapping_intervals


class TestWebAppSecurityAndDomain(unittest.TestCase):
    """Test suite verifying web security validation and pure interval calculation."""

    def test_sanitize_filename_traversal(self):
        """Rejects directory traversal characters and isolates basename."""
        malicious = "../../../etc/passwd"
        self.assertEqual(sanitize_filename(malicious), "passwd")

        windows_malicious = "..\\..\\windows\\system32\\cmd.exe"
        self.assertEqual(sanitize_filename(windows_malicious), "cmd.exe")

    def test_validate_file_extension(self):
        """Permits whitelisted extensions and rejects unapproved types."""
        allowed = (".mp3", ".wav", ".mp4")
        self.assertTrue(validate_file_extension("audio.mp3", allowed))
        self.assertTrue(validate_file_extension("VIDEO.MP4", allowed))
        self.assertFalse(validate_file_extension("script.sh", allowed))
        self.assertFalse(validate_file_extension("malware.exe", allowed))

    def test_validate_file_size(self):
        """Enforces upload payload boundaries."""
        max_bytes = 1000
        self.assertTrue(validate_file_size(500, max_bytes))
        self.assertFalse(validate_file_size(0, max_bytes))
        self.assertFalse(validate_file_size(1001, max_bytes))

    def test_generate_job_id(self):
        """Generates 32-character hexadecimal random tokens."""
        job_id = generate_secure_job_id()
        self.assertEqual(len(job_id), 32)
        int(job_id, 16)  # Verifies hex format

    def test_calculate_segments_silence_cut(self):
        """Verifies dead air excision with margin padding."""
        settings = ProcessingSettings(min_silence_duration=1.0, margin_padding=0.1, mode="cut")
        silences = [SilenceInterval(start=10.0, end=15.0)]
        segments = calculate_segments(total_duration=30.0, silence_intervals=silences, settings=settings)

        self.assertEqual(len(segments), 2)
        self.assertAlmostEqual(segments[0].start, 0.0)
        self.assertAlmostEqual(segments[0].end, 10.1)
        self.assertAlmostEqual(segments[1].start, 14.9)
        self.assertAlmostEqual(segments[1].end, 30.0)


if __name__ == "__main__":
    unittest.main()
