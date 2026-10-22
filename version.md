# Version history

## Unreleased

### Added
- Native Desktop GUI application for cutting or shortening dead air in sound files.
- FFmpeg-driven silence detection (`silencedetect`) with configurable dB threshold, minimum silence duration, and margin padding.
- Dual silence reduction modes: full silence stripping and natural pause truncation (shortening dead air to a configurable pause length).
- Audio preset profiles: "Podcast / Voiceover", "Aggressive Cut", and "Subtle Breath Retain".
- Pre-export "Scan / Preview" capability calculating exact time saved, silence interval count, and predicted new duration.
- Batch queue processing supporting multi-file and whole-folder ingestion for MP3, WAV, FLAC, AAC, M4A, and OGG formats.
- Safe non-destructive output pipeline with configurable target folder and filename suffix.
- Dedicated Sound Power Cutoff slider with dynamic subtitle guidance to cut zones where sound power <= threshold.
- Integrated FFmpeg `volumedetect` to measure and display Mean Sound Power and Peak Sound Power in the scan preview panel.
- Expanded slider ranges (-70.0 dB to -5.0 dB for sound power, 0.05s to 3.0s for zone duration).
- Full Video Mode: Ingest and process video files (MP4, MKV, MOV, AVI, WEBM, FLV, WMV, M4V, TS), cutting dead air while keeping video frames and audio synchronized with zero drift.
- Video Mode settings panel with quality presets (High Quality CRF 18, Fast CRF 22, Compact CRF 26, Draft Ultrafast).
- Optional audio-only extraction mode (.mp3) from video inputs.
- Visual media badges ([VIDEO] / [AUDIO]) in queue list and media type indicator in scan preview panel.
- Browser-based web application edition in `web-app/` with two-color black-and-white theme, drag-and-drop media upload, pre-flight scanner, and download streaming.
### Fixed
- Corrected mode change handler in GUI to use frame packing/unpacking instead of calling unsupported -state on container frames.
