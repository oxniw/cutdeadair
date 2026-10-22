# ==============================================================================
# File: .//Description-of-file/render_video.md
# Overview: Video rendering engine slicing and concatenating video frames and audio streams synchronously using FFmpeg.
# ==============================================================================

import os
import subprocess
import tempfile
from typing import List, Callable, Optional
from domain_models import KeepSegment


def _render_video_single_chunk(
    input_path: str,
    output_path: str,
    segments: List[KeepSegment],
    video_preset: str = "fast",
    video_crf: int = 22,
) -> None:
    """Renders video and audio segments in a single FFmpeg invocation."""
    num_segs = len(segments)

    if num_segs == 1 and segments[0].start <= 0.001:
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i", input_path,
            "-ss", f"{segments[0].start:.3f}",
            "-to", f"{segments[0].end:.3f}",
            "-c:v", "libx264",
            "-preset", video_preset,
            "-crf", str(video_crf),
            "-c:a", "aac",
            "-b:a", "192k",
            output_path,
        ]
    else:
        filter_parts = []
        concat_inputs = []

        for idx, seg in enumerate(segments):
            v_label = f"v{idx}"
            a_label = f"a{idx}"
            filter_parts.append(
                f"[0:v]trim=start={seg.start:.3f}:end={seg.end:.3f},setpts=PTS-STARTPTS[{v_label}];"
                f"[0:a]atrim=start={seg.start:.3f}:end={seg.end:.3f},asetpts=PTS-STARTPTS[{a_label}];"
            )
            concat_inputs.append(f"[{v_label}][{a_label}]")

        concat_clause = f"{''.join(concat_inputs)}concat=n={num_segs}:v=1:a=1[outv][outa]"
        filter_complex_str = "".join(filter_parts) + concat_clause

        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i", input_path,
            "-filter_complex", filter_complex_str,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", video_preset,
            "-crf", str(video_crf),
            "-c:a", "aac",
            "-b:a", "192k",
            output_path,
        ]

    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg video rendering failed: {process.stderr}")


def render_video(
    input_path: str,
    output_path: str,
    keep_segments: List[KeepSegment],
    video_preset: str = "fast",
    video_crf: int = 22,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> str:
    """Renders video and audio segments with frame synchronization."""
    if not keep_segments:
        raise ValueError("Cannot render video: keep_segments is empty.")

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    total_segments = len(keep_segments)
    CHUNK_SIZE = 60

    if total_segments <= CHUNK_SIZE:
        if progress_callback:
            progress_callback(0.2, f"Synchronizing {total_segments} video/audio segments...")

        _render_video_single_chunk(
            input_path=input_path,
            output_path=output_path,
            segments=keep_segments,
            video_preset=video_preset,
            video_crf=video_crf,
        )

        if progress_callback:
            progress_callback(1.0, "Video rendering complete.")
        return output_path

    temp_dir = tempfile.mkdtemp(prefix="web_deadair_vid_")
    chunk_files: List[str] = []

    try:
        num_chunks = (total_segments + CHUNK_SIZE - 1) // CHUNK_SIZE

        for chunk_idx in range(num_chunks):
            start_i = chunk_idx * CHUNK_SIZE
            end_i = min(start_i + CHUNK_SIZE, total_segments)
            sub_segments = keep_segments[start_i:end_i]

            chunk_filename = os.path.join(temp_dir, f"chunk_{chunk_idx:04d}.mp4")
            chunk_files.append(chunk_filename)

            if progress_callback:
                frac = (chunk_idx / num_chunks) * 0.85
                progress_callback(frac, f"Rendering video part {chunk_idx + 1}/{num_chunks}...")

            _render_video_single_chunk(
                input_path=input_path,
                output_path=chunk_filename,
                segments=sub_segments,
                video_preset=video_preset,
                video_crf=video_crf,
            )

        manifest_path = os.path.join(temp_dir, "manifest.txt")
        with open(manifest_path, "w", encoding="utf-8") as f:
            for c_path in chunk_files:
                clean_path = c_path.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        if progress_callback:
            progress_callback(0.9, "Joining video parts...")

        concat_cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-f", "concat",
            "-safe", "0",
            "-i", manifest_path,
            "-c", "copy",
            output_path,
        ]

        result = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg chunk joining failed: {result.stderr}")

        if progress_callback:
            progress_callback(1.0, "Video rendering complete.")

        return output_path

    finally:
        if os.path.exists(temp_dir):
            for fname in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, fname))
                except OSError:
                    pass
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass
