# Description: system_resources.py

## Overview
Dynamic hardware and container resource inspection module measuring available memory across Linux Cgroups v2 (modern Docker/Render), Linux Cgroups v1, Linux `/proc/meminfo`, and Windows `GlobalMemoryStatusEx`. Dynamically computes safe rendering budgets, worker counts, and thread limits without exceeding available memory.

## Exports & Functions
- `get_available_memory_mb() -> float`
  - **Description**: Probes container cgroups limits and host operating system physical memory.
  - **Returns**: Measured available memory in megabytes (float).
- `calculate_render_budget(is_video: bool = True) -> RenderBudget`
  - **Description**: Computes worker pool concurrency, encoding threads per worker, and usable memory budget while enforcing a hard safety margin (minimum 32-64 MB) to prevent out-of-memory (OOM) errors.
  - **Parameters**: `is_video: bool` (default True).
  - **Returns**: Immutable `RenderBudget` dataclass instance containing `available_mb`, `usable_mb`, `workers`, `threads_per_worker`, and `safety_margin_mb`.

## Dependencies & Data Flow
- **Imports**: `os`, `sys`, `ctypes`, `domain_models.RenderBudget`.
- **Invoked By**: `render_video.py`, `process_media.py`.
- **Data Flow**: System cgroups/APIs -> memory measurement -> concurrency budget -> rendering thread pool.
