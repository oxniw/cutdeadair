# ==============================================================================
# File: .//Description-of-file/detect_silence.md
# Overview: Media detection adapter querying durations, silence timestamps, sound power levels, and video stream status.
# ==============================================================================

import re
import subprocess
from typing import List, Tuple
from domain_models import SilenceInterval


def get_audio_duration(file_path: str) -> float:
    """Queries FFprobe to retrieve total media duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as err:
        raise RuntimeError(f"FFprobe duration check failed for '{file_path}': {err}") from err


def detect_silence(
    file_path: str,
    threshold_db: float,
    min_silence_duration: float,
    total_duration: float,
) -> List[SilenceInterval]:
    """Executes FFmpeg silencedetect and returns detected dead air intervals."""
    filter_arg = f"silencedetect=noise={threshold_db}dB:d={min_silence_duration}"
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-vn",
        "-i", file_path,
        "-af", filter_arg,
        "-f", "null",
        "-",
    ]

    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"FFmpeg silence detection failed: {err.stderr}") from err

    re_start = re.compile(r"silence_start:\s*([0-9\.]+)")
    re_end = re.compile(r"silence_end:\s*([0-9\.]+)")

    intervals: List[SilenceInterval] = []
    current_start: float | None = None

    for line in process.stderr.splitlines():
        start_match = re_start.search(line)
        if start_match:
            current_start = float(start_match.group(1))

        end_match = re_end.search(line)
        if end_match:
            end_time = float(end_match.group(1))
            if current_start is not None:
                intervals.append(SilenceInterval(start=current_start, end=end_time))
                current_start = None

    if current_start is not None and current_start < total_duration:
        intervals.append(SilenceInterval(start=current_start, end=total_duration))

    return intervals


def measure_audio_volume(file_path: str) -> Tuple[float | None, float | None]:
    """Measures mean and peak volume in dBFS using FFmpeg volumedetect."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-vn",
        "-i", file_path,
        "-af", "volumedetect",
        "-f", "null",
        "-",
    ]
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        re_mean = re.search(r"mean_volume:\s*([-\d\.]+)\s*dB", process.stderr)
        re_max = re.search(r"max_volume:\s*([-\d\.]+)\s*dB", process.stderr)

        mean_db = float(re_mean.group(1)) if re_mean else None
        max_db = float(re_max.group(1)) if re_max else None
        return mean_db, max_db
    except Exception:
        return None, None


def is_video_file(file_path: str) -> bool:
    """Checks whether the media container contains a video stream."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "video" in result.stdout.lower()
    except Exception:
        return False
