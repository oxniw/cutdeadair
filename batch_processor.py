# ==============================================================================
# File: .//Description-of-file/batch_processor.md
# Overview: Batch orchestration pipeline processing multiple audio files with progress callbacks and cancellation support.
# ==============================================================================

from typing import List, Callable, Optional
from domain_models import ProcessingSettings, ProcessSummary
from process_audio_file import process_audio_file


def process_batch(
    files: List[str],
    settings: ProcessingSettings,
    on_file_start: Optional[Callable[[int, int, str], None]] = None,
    on_file_progress: Optional[Callable[[int, int, float, str], None]] = None,
    on_file_complete: Optional[Callable[[int, int, ProcessSummary], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
) -> List[ProcessSummary]:
    """
    Sequentially processes a queue of audio files with fine-grained callbacks.

    Args:
        files: List of file paths to process.
        settings: Processing configuration.
        on_file_start: Callback (index, total, file_path).
        on_file_progress: Callback (index, total, fraction, message).
        on_file_complete: Callback (index, total, summary).
        is_cancelled: Function returning True if execution was cancelled by user.

    Returns:
        List of ProcessSummary objects for all processed files.
    """
    summaries: List[ProcessSummary] = []
    total_files = len(files)

    for idx, file_path in enumerate(files, start=1):
        if is_cancelled and is_cancelled():
            break

        if on_file_start:
            on_file_start(idx, total_files, file_path)

        def file_progress_cb(fraction: float, message: str) -> None:
            if on_file_progress:
                on_file_progress(idx, total_files, fraction, message)

        summary = process_audio_file(
            file_path=file_path,
            settings=settings,
            progress_callback=file_progress_cb,
        )
        summaries.append(summary)

        if on_file_complete:
            on_file_complete(idx, total_files, summary)

    return summaries
