# ==============================================================================
# File: .//Description-of-file/render_audio.md
# Overview: Audio rendering engine using FFmpeg aselect and asetpts filter pipeline to slice keep segments into clean output.
# ==============================================================================

import os
import subprocess
from typing import List, Callable, Optional
from domain_models import KeepSegment


def render_audio(
    input_path: str,
    output_path: str,
    keep_segments: List[KeepSegment],
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> str:
    """
    Renders the specified KeepSegments into the final audio file using FFmpeg.

    Args:
        input_path: Path to the original audio file.
        output_path: Path where the processed file should be written.
        keep_segments: Non-overlapping spans to splice together.
        progress_callback: Optional callback reporting (fraction: 0.0-1.0, status_message: str).

    Returns:
        The verified absolute path to the generated output file.
    """
    if not keep_segments:
        raise ValueError("Cannot render audio: keep_segments list is empty (entire file was classified as silence).")

    # Ensure parent output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    # If only one segment that starts at 0 and covers the whole audio, copy or encode directly
    if len(keep_segments) == 1 and keep_segments[0].start <= 0.001:
        if progress_callback:
            progress_callback(0.5, "Exporting audio stream...")

        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i", input_path,
            "-ss", f"{keep_segments[0].start:.3f}",
            "-to", f"{keep_segments[0].end:.3f}",
            "-vn",
            output_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg render error: {result.stderr}")

        if progress_callback:
            progress_callback(1.0, "Complete!")
        return output_path

    if progress_callback:
        progress_callback(0.2, f"Preparing filtergraph for {len(keep_segments)} speech segments...")

    # Build aselect filter clause with between conditions
    conditions = "+".join(f"between(t,{seg.start:.3f},{seg.end:.3f})" for seg in keep_segments)
    filter_expr = f"aselect='{conditions}',asetpts=N/SR/TB"

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-i", input_path,
        "-af", filter_expr,
        "-vn",
        output_path,
    ]

    if progress_callback:
        progress_callback(0.6, "Rendering audio cut with FFmpeg...")

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg rendering failed: {process.stderr}")

    if progress_callback:
        progress_callback(1.0, "Render complete.")

    return output_path
