# ==============================================================================
# File: .//Description-of-file/main.md
# Overview: Application entry point initializing Tkinter desktop GUI and running main event loop.
# ==============================================================================

import shutil
import sys
import tkinter as tk
from tkinter import messagebox

from gui_components import DeadAirCutterGUI


def verify_dependencies() -> bool:
    """Verifies that external audio binaries (ffmpeg and ffprobe) are accessible in system PATH."""
    missing = []
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    if not shutil.which("ffprobe"):
        missing.append("ffprobe")

    if missing:
        msg = (
            f"Missing required audio utility: {', '.join(missing)}.\n\n"
            "Please ensure FFmpeg is installed and added to your system PATH environment variable."
        )
        print(f"Error: {msg}", file=sys.stderr)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Dependency Error", msg)
        root.destroy()
        return False
    return True


def main() -> None:
    """Entry point initializing the Tkinter root and mounting DeadAirCutterGUI."""
    if not verify_dependencies():
        sys.exit(1)

    root = tk.Tk()
    app = DeadAirCutterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
