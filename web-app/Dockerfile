# ==============================================================================
# Dockerfile: CutDeadAir Web Application
# Description: Production container image with FFmpeg and Python 3.12 running under an unprivileged user.
# ==============================================================================

FROM python:3.12-slim

# Prevent python from buffering standard output/error
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    HOST=0.0.0.0

# Install FFmpeg and FFprobe binary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged application user
RUN useradd -m -u 10001 -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Create necessary storage directories and assign ownership to appuser
RUN mkdir -p /app/storage/uploads /app/storage/processed /app/storage/jobs \
    && chown -R appuser:appuser /app

# Copy application files
COPY --chown=appuser:appuser . /app/

# Switch to non-root execution context
USER appuser

# Expose HTTP port
EXPOSE 8080

# Run standard library ThreadingHTTPServer entry point
CMD ["python", "main.py"]
