# ==============================================================================
# File: .//Description-of-file/test_calculate_segments.md
# Overview: Unit tests validating the pure domain logic in calculate_segments and interval merging.
# ==============================================================================

import unittest
from domain_models import SilenceInterval, KeepSegment, ProcessingSettings
from calculate_segments import calculate_segments, merge_overlapping_intervals


class TestCalculateSegments(unittest.TestCase):
    """Unit test suite for silence excision and pause shortening arithmetic."""

    def test_no_silence_keeps_whole_file(self):
        """When no silences are identified, the entire audio duration is retained."""
        settings = ProcessingSettings()
        segments = calculate_segments(total_duration=100.0, silence_intervals=[], settings=settings)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].start, 0.0)
        self.assertEqual(segments[0].end, 100.0)

    def test_single_silence_cut_mode(self):
        """Validates that a silence in the middle is excised with margin buffer applied."""
        settings = ProcessingSettings(
            min_silence_duration=1.0,
            margin_padding=0.1,
            mode="cut",
        )
        # Silence from 10.0 to 15.0 in a 30s file
        silence = [SilenceInterval(start=10.0, end=15.0)]
        segments = calculate_segments(total_duration=30.0, silence_intervals=silence, settings=settings)

        self.assertEqual(len(segments), 2)
        # Sound 1: 0 to 10.0 + 0.1 margin = 10.1
        self.assertAlmostEqual(segments[0].start, 0.0)
        self.assertAlmostEqual(segments[0].end, 10.1)
        # Sound 2: 15.0 - 0.1 margin = 14.9 to 30.0
        self.assertAlmostEqual(segments[1].start, 14.9)
        self.assertAlmostEqual(segments[1].end, 30.0)

    def test_shorten_mode_target_pause(self):
        """Validates that shortening mode leaves the target pause duration between speech blocks."""
        settings = ProcessingSettings(
            min_silence_duration=1.0,
            target_pause=0.4,
            margin_padding=0.1,  # half_pause is 0.2, so padding is 0.2
            mode="shorten",
        )
        silence = [SilenceInterval(start=10.0, end=20.0)]  # 10s of dead air
        segments = calculate_segments(total_duration=30.0, silence_intervals=silence, settings=settings)

        self.assertEqual(len(segments), 2)
        # Sound 1 extends to 10.0 + 0.2 = 10.2
        self.assertAlmostEqual(segments[0].end, 10.2)
        # Sound 2 begins at 20.0 - 0.2 = 19.8
        self.assertAlmostEqual(segments[1].start, 19.8)

        # Concatenated pause is (10.2 - 10.0) + (20.0 - 19.8) = 0.2 + 0.2 = 0.4s
        retained_pause = (segments[0].end - 10.0) + (20.0 - segments[1].start)
        self.assertAlmostEqual(retained_pause, 0.4)

    def test_merge_overlapping_silences(self):
        """Validates that overlapping or abutting silence intervals are merged cleanly."""
        raw = [
            SilenceInterval(start=2.0, end=5.0),
            SilenceInterval(start=4.0, end=8.0),
            SilenceInterval(start=10.0, end=12.0),
        ]
        merged = merge_overlapping_intervals(raw)
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0], SilenceInterval(start=2.0, end=8.0))
        self.assertEqual(merged[1], SilenceInterval(start=10.0, end=12.0))

    def test_silence_at_audio_edges(self):
        """Tests that silence at the very start (0.0) and end (total_duration) is trimmed safely."""
        settings = ProcessingSettings(min_silence_duration=0.5, margin_padding=0.05, mode="cut")
        silences = [
            SilenceInterval(start=0.0, end=3.0),
            SilenceInterval(start=25.0, end=30.0),
        ]
        segments = calculate_segments(total_duration=30.0, silence_intervals=silences, settings=settings)
        self.assertEqual(len(segments), 1)
        # Speech was 3.0 to 25.0 -> with margin: max(0, 3.0 - 0.05) to min(30, 25.0 + 0.05)
        self.assertAlmostEqual(segments[0].start, 2.95)
        self.assertAlmostEqual(segments[0].end, 25.05)


if __name__ == "__main__":
    unittest.main()
