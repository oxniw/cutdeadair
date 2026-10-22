# ==============================================================================
# File: .//Description-of-file/process_audio_file.md
# Overview: Orchestrates end-to-end scanning, output path resolution, and rendering for a single audio file.
# ==============================================================================

import os
from typing import Callable, Optional
from config import DEFAULT_OUTPUT_SUBFOLDER, DEFAULT_OUTPUT_SUFFIX
from domain_models import ProcessingSettings, ProcessSummary, AudioScanResult
from scan_audio import scan_audio
from render_audio import render_audio
from render_video import render_video
from detect_silence import get_audio_duration


def build_output_path(input_path: str, settings: ProcessingSettings, is_video: bool = False) -> str:
    """
    Constructs the target output filepath based on user settings and input file location.

    Args:
        input_path: Path to the original audio/video file.
        settings: Processing settings with optional output_dir and output_suffix.
        is_video: Whether the input file has a video stream.

    Returns:
        Target output file path.
    """
    abs_input = os.path.abspath(input_path)
    dirname, basename = os.path.split(abs_input)
    root_name, ext = os.path.splitext(basename)

    # If extracting audio from a video, change output extension to .mp3
    if is_video and settings.export_audio_only:
        ext = ".mp3"

    suffix = settings.output_suffix if settings.output_suffix is not None else DEFAULT_OUTPUT_SUFFIX
    out_filename = f"{root_name}{suffix}{ext}"

    if settings.output_dir:
        target_dir = os.path.abspath(settings.output_dir)
    else:
        target_dir = os.path.join(dirname, DEFAULT_OUTPUT_SUBFOLDER)

    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, out_filename)


def process_audio_file(
    file_path: str,
    settings: ProcessingSettings,
    scan_result: Optional[AudioScanResult] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> ProcessSummary:
    """
    Processes an individual audio or video file to cut dead air and render output.

    Args:
        file_path: Path to the input media file.
        settings: Processing settings.
        scan_result: Optional cached scan result to avoid duplicate analysis.
        progress_callback: Optional callback reporting (fraction, message).

    Returns:
        ProcessSummary detailing success status, time saved, video mode, and output path.
    """
    try:
        if scan_result is None:
            if progress_callback:
                progress_callback(0.1, "Analyzing dead air intervals...")
            scan_result = scan_audio(file_path, settings)

        output_path = build_output_path(file_path, settings, is_video=scan_result.is_video)

        if not scan_result.keep_segments:
            return ProcessSummary(
                file_path=file_path,
                output_path="",
                success=False,
                error_message="All audio detected as silence; no speech to output.",
                original_duration=scan_result.total_duration,
                is_video=scan_result.is_video,
            )

        # Dispatch to Video or Audio rendering engine
        if scan_result.is_video and not settings.export_audio_only:
            if progress_callback:
                progress_callback(0.3, "Rendering cut video & synchronized audio...")

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

        # Confirm output duration with FFprobe
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
