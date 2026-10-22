# ==============================================================================
# File: .//Description-of-file/calculate_segments.md
# Overview: Pure algorithmic domain function calculating audio segments to keep based on silence intervals and user settings.
# ==============================================================================

from typing import List
from domain_models import SilenceInterval, KeepSegment, ProcessingSettings


def merge_overlapping_intervals(intervals: List[SilenceInterval]) -> List[SilenceInterval]:
    """Merges sorted overlapping or adjacent silence intervals into unified spans."""
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda x: x.start)
    merged: List[SilenceInterval] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        previous = merged[-1]
        if current.start <= previous.end:
            # Overlapping or abutting: merge into a single extended interval
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
    Computes list of KeepSegment spans to retain in the rendered audio.

    Args:
        total_duration: Total length of the audio file in seconds.
        silence_intervals: Identified intervals of dead air.
        settings: Processing settings (mode, padding, target pause, min duration).

    Returns:
        List of non-overlapping, ordered KeepSegment objects.
    """
    if total_duration <= 0.0:
        return []

    # Filter out silence intervals shorter than the minimum silence duration threshold
    significant_silences = [
        s for s in silence_intervals
        if (s.end - s.start) >= settings.min_silence_duration
    ]

    # Merge any overlapping intervals
    merged_silences = merge_overlapping_intervals(significant_silences)

    if not merged_silences:
        # No dead air detected: keep entire audio unchanged
        return [KeepSegment(start=0.0, end=total_duration)]

    # Derive speech/sound intervals between silences
    raw_sound_intervals: List[KeepSegment] = []
    current_pos = 0.0

    for silence in merged_silences:
        # Clamp silence boundaries to valid audio duration
        s_start = max(0.0, min(total_duration, silence.start))
        s_end = max(0.0, min(total_duration, silence.end))

        if s_start > current_pos:
            raw_sound_intervals.append(KeepSegment(start=current_pos, end=s_start))
        current_pos = max(current_pos, s_end)

    if current_pos < total_duration:
        raw_sound_intervals.append(KeepSegment(start=current_pos, end=total_duration))

    # Apply padding / shortening logic based on selected mode
    adjusted_segments: List[KeepSegment] = []

    if settings.mode == "shorten":
        # Shorten: retain half the target pause on each side of the speech boundary
        half_pause = max(0.0, settings.target_pause / 2.0)
        padding = max(half_pause, settings.margin_padding)

        for sound in raw_sound_intervals:
            k_start = max(0.0, sound.start - padding)
            k_end = min(total_duration, sound.end + padding)
            adjusted_segments.append(KeepSegment(start=k_start, end=k_end))
    else:
        # Complete cut: apply margin padding around speech
        margin = max(0.0, settings.margin_padding)
        for sound in raw_sound_intervals:
            k_start = max(0.0, sound.start - margin)
            k_end = min(total_duration, sound.end + margin)
            adjusted_segments.append(KeepSegment(start=k_start, end=k_end))

    if not adjusted_segments:
        return []

    # Merge any keep segments that overlap due to padding expansion
    merged_keep: List[KeepSegment] = [adjusted_segments[0]]

    for current in adjusted_segments[1:]:
        previous = merged_keep[-1]
        if current.start <= previous.end:
            new_end = max(previous.end, current.end)
            merged_keep[-1] = KeepSegment(start=previous.start, end=new_end)
        else:
            merged_keep.append(current)

    # Filter out empty or micro-duration segments (e.g. less than 5ms)
    filtered_keep = [s for s in merged_keep if (s.end - s.start) > 0.005]

    return filtered_keep
