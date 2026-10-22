# ==============================================================================
# File: .//Description-of-file/domain_models.md
# Overview: Typed data structures defining silence windows, keep segments, scan metrics, and rendering summaries.
# ==============================================================================

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SilenceInterval:
    """An interval of detected silence in seconds."""
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass(frozen=True)
class KeepSegment:
    """An interval of audio/video to retain in the rendered output."""
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class ProcessingSettings:
    """Configuration parameters for detection and rendering."""
    threshold_db: float = -32.0
    min_silence_duration: float = 0.6
    margin_padding: float = 0.15
    target_pause: float = 0.3
    mode: str = "shorten"  # "shorten" or "cut"
    export_audio_only: bool = False
    video_preset: str = "fast"
    video_crf: int = 22


@dataclass
class MediaScanResult:
    """Analysis result returned before final media rendering."""
    file_path: str
    total_duration: float
    silence_intervals: List[SilenceInterval] = field(default_factory=list)
    keep_segments: List[KeepSegment] = field(default_factory=list)
    mean_power_db: Optional[float] = None
    max_power_db: Optional[float] = None
    is_video: bool = False

    @property
    def total_silence_duration(self) -> float:
        return sum(i.duration for i in self.silence_intervals)

    @property
    def estimated_output_duration(self) -> float:
        return sum(s.duration for s in self.keep_segments)

    @property
    def time_saved(self) -> float:
        return max(0.0, self.total_duration - self.estimated_output_duration)

    @property
    def percentage_saved(self) -> float:
        if self.total_duration <= 0.0:
            return 0.0
        return (self.time_saved / self.total_duration) * 100.0


@dataclass
class ProcessSummary:
    """Outcome of a completed media processing job."""
    file_path: str
    output_path: str
    success: bool
    error_message: Optional[str] = None
    original_duration: float = 0.0
    processed_duration: float = 0.0
    is_video: bool = False

    @property
    def time_saved(self) -> float:
        return max(0.0, self.original_duration - self.processed_duration)
