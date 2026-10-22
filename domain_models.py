# ==============================================================================
# File: .//Description-of-file/domain_models.md
# Overview: Pure domain data structures representing audio intervals, segments, scan results, and configuration settings.
# ==============================================================================

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SilenceInterval:
    """Represents an identified dead air / silence interval in seconds."""
    start: float
    end: float

    @property
    def duration(self) -> float:
        """Returns the length of the silence interval in seconds."""
        return max(0.0, self.end - self.start)


@dataclass(frozen=True)
class KeepSegment:
    """Represents a segment of audio to keep and render into the final output."""
    start: float
    end: float

    @property
    def duration(self) -> float:
        """Returns the length of the segment in seconds."""
        return max(0.0, self.end - self.start)


@dataclass
class ProcessingSettings:
    """Configurable processing parameters for detection and cutting."""
    threshold_db: float = -32.0
    min_silence_duration: float = 0.6
    margin_padding: float = 0.15
    target_pause: float = 0.3
    mode: str = "shorten"  # "cut" or "shorten"
    output_dir: Optional[str] = None
    output_suffix: str = "_cut"
    is_video_mode: bool = True           # Video Mode enabled
    export_audio_only: bool = False      # Extract audio only from video input
    video_preset: str = "fast"           # libx264 encoding preset
    video_crf: int = 22                  # Video quality factor (18-28)


@dataclass
class AudioScanResult:
    """Result of pre-flight silence analysis on a media file."""
    file_path: str
    total_duration: float
    silence_intervals: List[SilenceInterval] = field(default_factory=list)
    keep_segments: List[KeepSegment] = field(default_factory=list)
    mean_power_db: Optional[float] = None
    max_power_db: Optional[float] = None
    is_video: bool = False

    @property
    def total_silence_duration(self) -> float:
        """Total duration of raw detected silence."""
        return sum(interval.duration for interval in self.silence_intervals)

    @property
    def estimated_output_duration(self) -> float:
        """Total duration of audio kept after processing."""
        return sum(seg.duration for seg in self.keep_segments)

    @property
    def time_saved(self) -> float:
        """Calculated duration saved by cutting or shortening."""
        return max(0.0, self.total_duration - self.estimated_output_duration)

    @property
    def percentage_saved(self) -> float:
        """Percentage of the original file cut away as dead air."""
        if self.total_duration <= 0.0:
            return 0.0
        return (self.time_saved / self.total_duration) * 100.0


@dataclass
class ProcessSummary:
    """Outcome summary for a rendered media file."""
    file_path: str
    output_path: str
    success: bool
    error_message: Optional[str] = None
    original_duration: float = 0.0
    processed_duration: float = 0.0
    is_video: bool = False

    @property
    def time_saved(self) -> float:
        """Net media time eliminated."""
        return max(0.0, self.original_duration - self.processed_duration)
