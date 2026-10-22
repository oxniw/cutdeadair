# ==============================================================================
# File: .//Description-of-file/scan_audio.md
# Overview: Non-destructive pre-flight analysis scanner calculating dead air intervals, segment cuts, and savings statistics.
# ==============================================================================

from domain_models import AudioScanResult, ProcessingSettings
from detect_silence import get_audio_duration, detect_silence, measure_audio_volume, is_video_file
from calculate_segments import calculate_segments


def scan_audio(file_path: str, settings: ProcessingSettings) -> AudioScanResult:
    """
    Performs pre-flight silence detection and segment calculation for an audio or video file.

    Args:
        file_path: Path to the audio or video file.
        settings: Processing settings (threshold, durations, mode).

    Returns:
        AudioScanResult containing duration, silence intervals, keep segments, power levels, video flag, and savings.
    """
    duration = get_audio_duration(file_path)
    mean_power, max_power = measure_audio_volume(file_path)
    is_vid = is_video_file(file_path) if settings.is_video_mode else False

    silence_intervals = detect_silence(
        file_path=file_path,
        threshold_db=settings.threshold_db,
        min_silence_duration=settings.min_silence_duration,
        total_duration=duration,
    )

    keep_segments = calculate_segments(
        total_duration=duration,
        silence_intervals=silence_intervals,
        settings=settings,
    )

    return AudioScanResult(
        file_path=file_path,
        total_duration=duration,
        silence_intervals=silence_intervals,
        keep_segments=keep_segments,
        mean_power_db=mean_power,
        max_power_db=max_power,
        is_video=is_vid,
    )

