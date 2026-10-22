# ==============================================================================
# File: .//Description-of-file/calculate_segments.md
# Overview: Algorithmic interval arithmetic calculating spans of sound to keep, pause shortening, and boundary padding.
# ==============================================================================

from typing import List
from domain_models import SilenceInterval, KeepSegment, ProcessingSettings


def merge_overlapping_intervals(intervals: List[SilenceInterval]) -> List[SilenceInterval]:
    """Merges sorted overlapping or abutting silence intervals."""
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda x: x.start)
    merged: List[SilenceInterval] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        previous = merged[-1]
        if current.start <= previous.end:
            new_end = max(previous.end, current.end)
            merged[-1] = SilenceInterval(start=previous.start, end=new_end)
        else:
            merged.append(current)

    return merged


def calculate_segments(
    total_duration: float,
    silence_intervals: List[SilenceInterval],
    settings: ProcessingSettings,
) -> List[KeepSegment]:
    """
    Computes list of KeepSegment spans to retain in the rendered output.
    Operates in memory without file system access.
    """
    if total_duration <= 0.0:
        return []

    significant_silences = [
        s for s in silence_intervals
        if (s.end - s.start) >= settings.min_silence_duration
    ]

    merged_silences = merge_overlapping_intervals(significant_silences)

    if not merged_silences:
        return [KeepSegment(start=0.0, end=total_duration)]

    raw_sound_intervals: List[KeepSegment] = []
    current_pos = 0.0

    for silence in merged_silences:
        s_start = max(0.0, min(total_duration, silence.start))
        s_end = max(0.0, min(total_duration, silence.end))

        if s_start > current_pos:
            raw_sound_intervals.append(KeepSegment(start=current_pos, end=s_start))
        current_pos = max(current_pos, s_end)

    if current_pos < total_duration:
        raw_sound_intervals.append(KeepSegment(start=current_pos, end=total_duration))

    adjusted_segments: List[KeepSegment] = []

    if settings.mode == "shorten":
        half_pause = max(0.0, settings.target_pause / 2.0)
        padding = max(half_pause, settings.margin_padding)

        for sound in raw_sound_intervals:
            k_start = max(0.0, sound.start - padding)
            k_end = min(total_duration, sound.end + padding)
            adjusted_segments.append(KeepSegment(start=k_start, end=k_end))
    else:
        margin = max(0.0, settings.margin_padding)
        for sound in raw_sound_intervals:
            k_start = max(0.0, sound.start - margin)
            k_end = min(total_duration, sound.end + margin)
            adjusted_segments.append(KeepSegment(start=k_start, end=k_end))

    if not adjusted_segments:
        return []

    merged_keep: List[KeepSegment] = [adjusted_segments[0]]

    for current in adjusted_segments[1:]:
        previous = merged_keep[-1]
        if current.start <= previous.end:
            new_end = max(previous.end, current.end)
            merged_keep[-1] = KeepSegment(start=previous.start, end=new_end)
        else:
            merged_keep.append(current)

    return [s for s in merged_keep if (s.end - s.start) > 0.005]
