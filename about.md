# About this project

## Purpose
A desktop software application that automatically detects and eliminates or shortens dead air (unwanted silences and pauses) in audio and video files such as podcasts, video interviews, lectures, YouTube recordings, and voiceovers.

## Audience
Content creators, video editors, podcasters, lecturers, and audio engineers looking to automate silence trimming across individual media files and multi-file queues without manual NLE or DAW editing.

## Product scope
- **Video Mode (Synchronized Video & Audio Cuts)**: Detects dead air in the audio track of video files and slices both video frames and sound in exact lockstep, preventing A/V sync drift.
- **Sound Power & Silence Detection**: Detects dead air segments where audio sound power falls below a configurable decibel cutoff slider (-70.0 dB to -5.0 dB) for a configurable minimum duration.
- **Audio Volume Analysis**: Measures and displays mean sound power and peak sound power in the preview panel to assist users in calibrating their cutoff slider.
- **Configurable Cut Modes**: Supports both complete dead air excision and natural pause shortening (e.g., shrinking pauses exceeding 1s down to a natural 0.3s room-tone pause).
- **Safety Padding & Cross-merging**: Configurable speech margin buffers around voiced speech to prevent clipped word beginnings or endings.
- **Audio Presets & Video Profiles**: Quick preset configurations alongside fine-tuning sliders and selectable video quality profiles (CRF 18-26, fast/ultrafast presets).
- **Audio Extraction Option**: Optional extraction of trimmed audio (.mp3) from video inputs.
- **Pre-flight Scan & Preview**: Fast pre-export scan displaying detected silence count, original duration, expected output duration, and percentage of time saved.
- **Batch Processing**: Multi-file and directory queue processing with progress reporting and cancellation.
- **Non-destructive Output**: Exports processed files with custom suffixes or to designated output directories while preserving original source files.
- **Explicit Non-goals**: Real-time microphone dead air suppression during live streaming, and speech-to-text transcript editing.

## Experience and theme
- **Interface**: Clean, desktop GUI built with Python standard Tkinter / TTK styling.
- **Layout**: Two-panel design featuring configuration and presets on the left/top, interactive file queue and scan preview on the right, and batch action controls with a progress indicator at the bottom.
- **Platform**: Native Windows desktop experience requiring no browser or internet connectivity.

## Technical constraints
- **Language & Runtime**: Python 3.12+ (standard library only; no pip dependencies required for GUI).
- **Media Engine**: FFmpeg / FFprobe integration via decoupled adapter interfaces (`silencedetect`, `volumedetect`, `trim`/`atrim`/`concat` filtergraph rendering).
- **Supported Formats**:
  - Audio: MP3, WAV, FLAC, AAC, M4A, OGG, WMA, AIFF.
  - Video: MP4, MKV, MOV, AVI, WEBM, FLV, WMV, M4V, TS.
- **File Architecture**: Strict adherence to modular single-responsibility scripts, unified `main.py` entry point, shared `config.py`, and synchronized `Description-of-file/` documentation.

## Quality, safety, and accessibility
- **Non-destructive Processing**: Original audio media files are never overwritten in-place without explicit configuration.
- **Memory Safety**: Filter script-based FFmpeg rendering operates without loading entire uncompressed multi-gigabyte audio waveforms into system RAM.
- **Deterministic Pure Logic**: Silence segment arithmetic and padding logic are completely decoupled from I/O and covered by automated unit tests.
