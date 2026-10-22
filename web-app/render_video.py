# ==============================================================================
# File: .//Description-of-file/render_video.md
# Overview: Memory-budgeted concurrent video rendering engine dynamically adjusting workers and threads to available RAM.
# ==============================================================================

import os  # Operating system file operations
import subprocess  # Subprocess execution for FFmpeg
import tempfile  # Temporary directory management
from concurrent.futures import ThreadPoolExecutor, as_completed  # Managed concurrent execution
from typing import List, Callable, Optional  # Type annotations
from domain_models import KeepSegment  # Domain model representing speech segment
from system_resources import calculate_render_budget  # Memory and worker budgeting


def _render_single_slice(
    input_path: str,  # Input media file path
    output_path: str,  # Output segment slice destination
    start: float,  # Segment start timestamp in seconds
    end: float,  # Segment end timestamp in seconds
    video_preset: str = "ultrafast",  # x264 preset minimizing memory lookahead
    video_crf: int = 22,  # Target video quality constant rate factor
    threads: int = 1,  # Worker thread count
) -> None:
    """Renders a single video slice using bounded memory and specified thread limit."""
    cmd = [  # Construct FFmpeg execution argument list
        "ffmpeg",  # Binary name
        "-y",  # Overwrite destination file without prompting
        "-hide_banner",  # Suppress banner output
        "-ss", f"{start:.3f}",  # Fast seek to start timestamp
        "-to", f"{end:.3f}",  # Cut up to end timestamp
        "-i", input_path,  # Input file path
        "-c:v", "libx264",  # Standard H.264 video codec
        "-preset", video_preset,  # Ultrafast preset avoids lookahead buffers
        "-crf", str(video_crf),  # Video quality level
        "-threads", str(max(1, threads)),  # Bounded thread allocation
        "-c:a", "aac",  # AAC audio codec
        "-b:a", "128k",  # Standard audio bitrate
        "-ar", "44100",  # Normalize sample rate across slices
        "-avoid_negative_ts", "make_zero",  # Shift timestamps to zero
        output_path,  # Output destination path
    ]  # End of command arguments

    process = subprocess.run(  # Execute FFmpeg subprocess synchronously
        cmd,  # Command list
        stdout=subprocess.PIPE,  # Capture standard output
        stderr=subprocess.PIPE,  # Capture standard error
        text=True,  # Decode text stream
    )  # Await process exit
    if process.returncode != 0:  # Check return code for error
        raise RuntimeError(f"FFmpeg slice rendering failed: {process.stderr}")  # Raise descriptive error


def render_video(
    input_path: str,  # Source video file path
    output_path: str,  # Final rendered media file path
    keep_segments: List[KeepSegment],  # Whitelisted time segments to retain
    video_preset: str = "ultrafast",  # Encoding preset default
    video_crf: int = 22,  # Encoding quality default
    progress_callback: Optional[Callable[[float, str], None]] = None,  # Progress reporter
) -> str:
    """Renders video segments concurrently within dynamic memory safety budgets."""
    if not keep_segments:  # Guard against empty segment lists
        raise ValueError("Cannot render video: keep_segments is empty.")  # Raise error

    valid_segments = [s for s in keep_segments if s.end > s.start]  # Filter out empty or negative spans
    if not valid_segments:  # Ensure at least one valid slice remains
        raise ValueError("Cannot render video: all segments have zero duration.")  # Raise error

    total_segments = len(valid_segments)  # Total number of slices to process
    output_dir = os.path.dirname(os.path.abspath(output_path))  # Resolve target directory
    os.makedirs(output_dir, exist_ok=True)  # Create target directory if needed

    # Calculate optimal memory budget and concurrency
    budget = calculate_render_budget(is_video=True)  # Dynamic resource inspection
    effective_workers = min(budget.workers, total_segments)  # Bounded worker pool

    # Fast path: single continuous segment
    if total_segments == 1:  # If only one segment exists
        if progress_callback:  # If callback supplied
            progress_callback(0.4, "Rendering single video segment...")  # Update progress
        _render_single_slice(  # Render directly to final output
            input_path=input_path,  # Source video
            output_path=output_path,  # Final target
            start=valid_segments[0].start,  # Start time
            end=valid_segments[0].end,  # End time
            video_preset=video_preset,  # Preset
            video_crf=video_crf,  # CRF
            threads=budget.threads_per_worker,  # Threads
        )  # Direct slice completed
        if progress_callback:  # If callback supplied
            progress_callback(1.0, "Video rendering complete.")  # Complete status
        return output_path  # Return output file path

    # Multi-segment path: parallel slice extraction followed by concat demuxer
    temp_dir = tempfile.mkdtemp(prefix="deadair_slice_")  # Create isolated temporary directory
    slice_files: List[str] = [  # Generate file paths for all slices
        os.path.join(temp_dir, f"slice_{i:05d}.mp4") for i in range(total_segments)
    ]  # Slices mapped

    try:  # Ensure cleanup upon completion or failure
        if progress_callback:  # Initial progress notification
            progress_callback(0.05, f"Allocated {effective_workers} workers ({budget.usable_mb:.0f} MB memory budget)...")

        completed_slices = 0  # Counter for completed tasks
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:  # Managed worker pool
            future_to_idx = {  # Submit slice tasks
                executor.submit(
                    _render_single_slice,
                    input_path,
                    slice_files[idx],
                    seg.start,
                    seg.end,
                    video_preset,
                    video_crf,
                    budget.threads_per_worker,
                ): idx
                for idx, seg in enumerate(valid_segments)
            }  # Tasks submitted

            for future in as_completed(future_to_idx):  # Await each slice completion
                future.result()  # Propagate any rendering exception
                completed_slices += 1  # Increment counter
                if progress_callback:  # Update progress
                    pct = 0.05 + (0.85 * (completed_slices / total_segments))  # Progress fraction
                    progress_callback(
                        pct,
                        f"Rendering slices: {completed_slices}/{total_segments} ({effective_workers} workers active)...",
                    )  # Progress message

        # Build FFmpeg concat demuxer manifest
        manifest_path = os.path.join(temp_dir, "manifest.txt")  # Path to concat manifest
        with open(manifest_path, "w", encoding="utf-8") as f:  # Write manifest file
            for s_path in slice_files:  # Loop through generated slice paths
                clean_path = s_path.replace("\\", "/")  # Normalize forward slashes for FFmpeg
                f.write(f"file '{clean_path}'\n")  # Write demuxer file line

        if progress_callback:  # Update progress for stitching phase
            progress_callback(0.92, "Joining video segments...")  # Status message

        # Stitch video slices with stream copy (instantaneous, zero re-encode, minimal memory)
        concat_cmd = [  # Concat command argument list
            "ffmpeg",  # Binary name
            "-y",  # Overwrite destination
            "-hide_banner",  # Suppress banner
            "-f", "concat",  # Use concat demuxer format
            "-safe", "0",  # Allow arbitrary file paths
            "-i", manifest_path,  # Pass manifest input
            "-c", "copy",  # Direct bitstream copy without decoding
            output_path,  # Final media output destination
        ]  # End of concat arguments

        result = subprocess.run(  # Execute concat demuxer
            concat_cmd,  # Command list
            stdout=subprocess.PIPE,  # Capture stdout
            stderr=subprocess.PIPE,  # Capture stderr
            text=True,  # Decode text stream
        )  # Wait for completion
        if result.returncode != 0:  # Check for error
            raise RuntimeError(f"FFmpeg chunk joining failed: {result.stderr}")  # Raise error

        if progress_callback:  # Report final completion
            progress_callback(1.0, "Video rendering complete.")  # Complete status

        return output_path  # Return path to processed video

    finally:  # Cleanup temporary slices and directory
        if os.path.exists(temp_dir):  # Verify temp directory exists
            for fname in os.listdir(temp_dir):  # Iterate across temp files
                try:  # Attempt deletion
                    os.remove(os.path.join(temp_dir, fname))  # Delete file
                except OSError:  # Ignore deletion errors
                    pass  # Pass
            try:  # Attempt directory removal
                os.rmdir(temp_dir)  # Remove empty directory
            except OSError:  # Ignore deletion errors
                pass  # Pass
