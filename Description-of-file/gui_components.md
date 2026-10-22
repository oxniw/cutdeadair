# Description: gui_components.py

## Overview
Tkinter / TTK Desktop GUI application class managing the window layout, preset dropdown, threshold sliders, interactive file queue, scan preview metrics, output destination controls, and background worker threads.

## Exports & Functions
- `class DeadAirCutterGUI`
  - **Description**: Main window controller managing user interactions and UI state.
  - **Methods**:
    - `__init__(root: tk.Tk)`: Builds UI widgets and applies initial preset.
    - `_configure_styles()`: Applies custom ttk themes and font weights.
    - `_build_layout()`: Arranges panels (left parameters, right queue, bottom actions).
    - `_build_settings_panel(parent)`: Constructs preset dropdown, Sound Power Cutoff slider, min duration, margin padding, mode radio buttons, pause duration slider, and Video Mode settings (sync toggle, audio-only extraction checkbox, and video quality preset dropdown).
    - `_build_queue_panel(parent)`: Builds queue listbox with [VIDEO]/[AUDIO] media badges, file/folder pickers, scan preview (duration, dead air, sound power, media type, sync mode), and destination options.
    - `_build_bottom_panel()`: Builds the progress bar, status label, and action buttons.
    - `_load_preset(name: str)`: Loads settings from configuration preset dictionaries.
    - `_scan_selected_file()`: Runs non-destructive scan in background daemon thread and displays time saved.
    - `_start_processing()`: Launches batch processing thread, updating progress bar and status asynchronously.
    - `_request_cancel()`: Sets cancellation flag to halt batch queue.

## Dependencies & Data Flow
- **Imports**: `os`, `threading`, `tkinter`, `tkinter.ttk`, `tkinter.filedialog`, `tkinter.messagebox`, `config.*`, `domain_models.*`, `scan_audio.scan_audio`, `batch_processor.process_batch`.
- **Invoked By**: `main.py`.
- **Data Flow**: Captures user inputs from UI controls -> converts to `ProcessingSettings` -> dispatches to background threads (`scan_audio`, `process_batch`) -> marshals updates back to UI mainloop via `root.after(...)`.
