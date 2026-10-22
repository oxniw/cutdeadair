# Description: system_resources.py

## Overview
Dynamic hardware and container resource inspection module measuring available memory and CPU quota fractions across Linux Cgroups v2 (Render and modern containers), Linux Cgroups v1, Linux `/proc/meminfo`, and Windows `GlobalMemoryStatusEx`. Dynamically computes safe rendering budgets, worker counts, and thread limits without starving server processes or triggering 502/OOM errors.

## Exports & Functions
- `get_available_memory_mb() -> float`
  - **Description**: Probes container cgroups limits and host operating system physical memory.
  - **Returns**: Measured available memory in megabytes (float).
- `get_available_cpu_quota() -> float`
  - **Description**: Inspects container CFS CPU quota (e.g. Render 0.1 CPU quota) or physical CPU core count.
  - **Returns**: Available CPU fraction or core count (float).
- `calculate_render_budget(is_video: bool = True) -> RenderBudget`
  - **Description**: Evaluates both CPU quota and usable memory. Limits worker concurrency to 1 on fractional CPU containers (like Render Free Tier 0.1 CPU) to prevent CPU starvation and gateway timeouts, while auto-scaling up to 6 workers on multi-core systems.
  - **Parameters**: `is_video: bool` (default True).
  - **Returns**: Immutable `RenderBudget` dataclass instance containing `available_mb`, `usable_mb`, `workers`, `threads_per_worker`, and `safety_margin_mb`.

## Dependencies & Data Flow
- **Imports**: `os`, `sys`, `ctypes`, `domain_models.RenderBudget`.
- **Invoked By**: `render_video.py`, `process_media.py`.
- **Data Flow**: System cgroups/APIs -> memory and CPU quota measurement -> concurrency budget -> rendering thread pool.
