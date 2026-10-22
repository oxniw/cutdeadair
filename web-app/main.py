# ==============================================================================
# File: .//Description-of-file/main.md
# Overview: Entry point initializing ThreadingHTTPServer on configured host/port and verifying audio/video binaries.
# ==============================================================================

import shutil
import sys
from http.server import ThreadingHTTPServer

from config import SERVER_HOST, SERVER_PORT
from server_router import DeadAirHTTPHandler


def verify_dependencies() -> bool:
    """Confirms availability of FFmpeg and FFprobe in system PATH."""
    missing = []
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    if not shutil.which("ffprobe"):
        missing.append("ffprobe")

    if missing:
        print(f"Error: Required binary not found: {', '.join(missing)}", file=sys.stderr)
        print("Please install FFmpeg and add it to system PATH.", file=sys.stderr)
        return False
    return True


def main() -> None:
    """Starts the multi-threaded web server."""
    if not verify_dependencies():
        sys.exit(1)

    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadingHTTPServer(server_address, DeadAirHTTPHandler)

    print("==================================================")
    print(f" CUTDEADAIR WEB APPLICATION")
    print(f" Running at: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f" Press Ctrl+C to stop.")
    print("==================================================")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
