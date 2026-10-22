# Description: main.py

## Overview
Primary application entry point responsible for environment validation (checking FFmpeg and FFprobe binary availability in PATH) and launching the Tkinter desktop GUI.

## Exports & Functions
- `verify_dependencies() -> bool`
  - **Description**: Verifies that both `ffmpeg` and `ffprobe` are present in the system PATH. Displays an alert dialog if missing.
  - **Parameters**: None.
  - **Returns**: `True` if all binaries are found; `False` otherwise.

- `main() -> None`
  - **Description**: Instantiates the Tkinter root window, attaches `DeadAirCutterGUI`, and starts `root.mainloop()`.
  - **Parameters**: None.
  - **Returns**: None.

## Dependencies & Data Flow
- **Imports**: `shutil`, `sys`, `tkinter`, `tkinter.messagebox`, `gui_components.DeadAirCutterGUI`.
- **Invoked By**: Executed directly by the user (`python main.py`).
- **Data Flow**: System environment -> checks audio binaries -> initializes UI event loop -> hands control over to `DeadAirCutterGUI`.
