# ==============================================================================
# File: .//Description-of-file/process_media.md
# Overview: Media pipeline coordinator managing pre-flight scanning, path resolution, and dispatching to video or audio renderers.
# ==============================================================================

import os
from typing import Callable, Optional
from domain_models import ProcessingSettings, ProcessSummary, MediaScanResult
from calculate_segments import calculate_segments
from detect_silence import get_audio_duration, detect_silence, measure_audio_volume, is_video_file
from render_audio import render_audio
from render_video import render_video


def scan_media(file_path: str, settings: ProcessingSettings) -> MediaScanResult:
    """Performs non-destructive pre-flight silence analysis and returns duration and savings."""
    duration = get_audio_duration(file_path)
    mean_power, max_power = measure_audio_volume(file_path)
    is_vid = is_video_file(file_path)

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

    return MediaScanResult(
        file_path=file_path,
        total_duration=duration,
        silence_intervals=silence_intervals,
        keep_segments=keep_segments,
        mean_power_db=mean_power,
        max_power_db=max_power,
        is_video=is_vid,
    )


def process_media(
    file_path: str,
    output_path: str,
    settings: ProcessingSettings,
    scan_result: Optional[MediaScanResult] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> ProcessSummary:
    """Renders processed media to the target output path."""
    try:
        if scan_result is None:
            if progress_callback:
                progress_callback(0.1, "Analyzing silence intervals...")
            scan_result = scan_media(file_path, settings)

        if not scan_result.keep_segments:
            return ProcessSummary(
                file_path=file_path,
                output_path="",
                success=False,
                error_message="Entire file detected as silence.",
                original_duration=scan_result.total_duration,
                is_video=scan_result.is_video,
            )

        if scan_result.is_video and not settings.export_audio_only:
            if progress_callback:
                progress_callback(0.3, "Rendering video and synchronized audio...")

            render_video(
                input_path=file_path,
                output_path=output_path,
                keep_segments=scan_result.keep_segments,
                video_preset=settings.video_preset,
                video_crf=settings.video_crf,
                progress_callback=progress_callback,
            )
        else:
            if progress_callback:
                progress_callback(0.4, "Rendering audio cut...")

            render_audio(
                input_path=file_path,
                output_path=output_path,
                keep_segments=scan_result.keep_segments,
                progress_callback=progress_callback,
            )

        processed_duration = get_audio_duration(output_path)

        return ProcessSummary(
            file_path=file_path,
            output_path=output_path,
            success=True,
            original_duration=scan_result.total_duration,
            processed_duration=processed_duration,
            is_video=scan_result.is_video,
        )

    except Exception as err:
        return ProcessSummary(
            file_path=file_path,
            output_path="",
            success=False,
            error_message=str(err),
        )
