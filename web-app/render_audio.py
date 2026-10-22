# ==============================================================================
# File: .//Description-of-file/render_audio.md
# Overview: Audio rendering engine slicing sound segments using FFmpeg aselect and asetpts filtergraphs.
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
    """Renders sliced audio segments into output path using FFmpeg."""
    if not keep_segments:
        raise ValueError("Cannot render audio: keep_segments is empty.")

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

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
            progress_callback(1.0, "Audio export complete.")
        return output_path

    if progress_callback:
        progress_callback(0.2, f"Filtering {len(keep_segments)} speech segments...")

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
        progress_callback(0.6, "Rendering audio cut...")

    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg rendering failed: {process.stderr}")

    if progress_callback:
        progress_callback(1.0, "Audio rendering complete.")

    return output_path
