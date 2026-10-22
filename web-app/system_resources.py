# ==============================================================================
# File: .//Description-of-file/system_resources.md
# Overview: Dynamic memory detection and CPU quota inspection determining safe concurrency budgets.
# ==============================================================================

import os  # Operating system interactions
import sys  # System platform information
import ctypes  # C-compatible data types for Windows memory querying
from domain_models import RenderBudget  # Typed render budget model


def get_available_memory_mb() -> float:
    """
    Measures available memory in megabytes across Linux cgroups (Docker/Render),
    Linux procfs, and Windows systems.
    """
    # 1. Inspect Linux Cgroups v2 (Render and modern container runtimes)
    cg2_max = "/sys/fs/cgroup/memory.max"  # Path to cgroups v2 memory maximum
    cg2_curr = "/sys/fs/cgroup/memory.current"  # Path to cgroups v2 current usage
    if os.path.exists(cg2_max) and os.path.exists(cg2_curr):  # Verify cgroups v2 paths
        try:  # Attempt read
            with open(cg2_max, "r", encoding="utf-8") as f:  # Read limit
                max_raw = f.read().strip()  # Strip whitespace
            with open(cg2_curr, "r", encoding="utf-8") as f:  # Read usage
                curr_raw = f.read().strip()  # Strip whitespace
            if max_raw != "max":  # Check if constrained
                max_bytes = int(max_raw)  # Parse limit integer
                curr_bytes = int(curr_raw)  # Parse current integer
                return max(16.0, (max_bytes - curr_bytes) / (1024.0 * 1024.0))  # Available in MB
        except Exception:  # Fall through on error
            pass  # Pass

    # 2. Inspect Linux Cgroups v1 (Legacy container runtimes)
    cg1_limit = "/sys/fs/cgroup/memory/memory.limit_in_bytes"  # Path to cgroups v1 limit
    cg1_usage = "/sys/fs/cgroup/memory/memory.usage_in_bytes"  # Path to cgroups v1 usage
    if os.path.exists(cg1_limit) and os.path.exists(cg1_usage):  # Verify cgroups v1 paths
        try:  # Attempt read
            with open(cg1_limit, "r", encoding="utf-8") as f:  # Read limit
                limit_bytes = int(f.read().strip())  # Parse integer
            with open(cg1_usage, "r", encoding="utf-8") as f:  # Read usage
                usage_bytes = int(f.read().strip())  # Parse integer
            if limit_bytes < (1 << 58):  # Check if constrained below infinite threshold
                return max(16.0, (limit_bytes - usage_bytes) / (1024.0 * 1024.0))  # Available in MB
        except Exception:  # Fall through on error
            pass  # Pass

    # 3. Inspect Linux Host /proc/meminfo
    if os.path.exists("/proc/meminfo"):  # Verify procfs presence
        try:  # Attempt read
            with open("/proc/meminfo", "r", encoding="utf-8") as f:  # Read meminfo
                for line in f:  # Iterate lines
                    if line.startswith("MemAvailable:"):  # Find available memory line
                        parts = line.split()  # Split words
                        return max(16.0, float(parts[1]) / 1024.0)  # Convert kB to MB
        except Exception:  # Fall through on error
            pass  # Pass

    # 4. Inspect Windows GlobalMemoryStatusEx via ctypes
    if sys.platform == "win32":  # If running under Windows
        try:  # Attempt Windows API call
            class MEMORYSTATUSEX(ctypes.Structure):  # Windows memory struct
                _fields_ = [  # Struct fields
                    ("dwLength", ctypes.c_ulong),  # Struct size
                    ("dwMemoryLoad", ctypes.c_ulong),  # Memory load pct
                    ("ullTotalPhys", ctypes.c_ulonglong),  # Total physical
                    ("ullAvailPhys", ctypes.c_ulonglong),  # Available physical
                    ("ullTotalPageFile", ctypes.c_ulonglong),  # Total page file
                    ("ullAvailPageFile", ctypes.c_ulonglong),  # Avail page file
                    ("ullTotalVirtual", ctypes.c_ulonglong),  # Total virtual
                    ("ullAvailVirtual", ctypes.c_ulonglong),  # Avail virtual
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),  # Extended virtual
                ]  # End struct fields
            stat = MEMORYSTATUSEX()  # Instantiate struct
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)  # Set struct length
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))  # Query Windows kernel
            return max(16.0, stat.ullAvailPhys / (1024.0 * 1024.0))  # Return available physical MB
        except Exception:  # Fall through on error
            pass  # Pass

    # 5. Safe conservative fallback
    return 256.0  # Conservative baseline in MB


def get_available_cpu_quota() -> float:
    """
    Detects available CPU quota fraction in containers (e.g. Render 0.1 CPU)
    or returns physical host CPU core count.
    """
    # 1. Linux Cgroups v2 cpu.max
    cg2_cpu = "/sys/fs/cgroup/cpu.max"  # Path to cgroups v2 cpu quota
    if os.path.exists(cg2_cpu):  # Verify presence
        try:  # Attempt read
            with open(cg2_cpu, "r", encoding="utf-8") as f:  # Open file
                parts = f.read().strip().split()  # Split quota and period
                if len(parts) >= 2 and parts[0] != "max":  # If quota constrained
                    quota = float(parts[0])  # Quota in microseconds
                    period = float(parts[1])  # Period in microseconds
                    if period > 0:  # Validate period
                        return max(0.1, quota / period)  # Return CPU fraction
        except Exception:  # Handle error
            pass  # Pass

    # 2. Linux Cgroups v1 CFS quota
    cg1_quota = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"  # Path to cgroups v1 quota
    cg1_period = "/sys/fs/cgroup/cpu/cpu.cfs_period_us"  # Path to cgroups v1 period
    if os.path.exists(cg1_quota) and os.path.exists(cg1_period):  # Verify presence
        try:  # Attempt read
            with open(cg1_quota, "r", encoding="utf-8") as f:  # Read quota
                q = float(f.read().strip())  # Parse quota
            with open(cg1_period, "r", encoding="utf-8") as f:  # Read period
                p = float(f.read().strip())  # Parse period
            if q > 0 and p > 0:  # If constrained
                return max(0.1, q / p)  # Return CPU fraction
        except Exception:  # Handle error
            pass  # Pass

    # 3. Host CPU core count
    return float(os.cpu_count() or 1)  # Fallback to physical cores


def calculate_render_budget(is_video: bool = True) -> RenderBudget:
    """
    Calculates concurrency workers, encoding threads, and memory budget
    by evaluating both available RAM and CPU quota limits.
    """
    avail_mb = get_available_memory_mb()  # Measure current available memory
    cpu_quota = get_available_cpu_quota()  # Measure CPU quota fraction

    # Reserve safety headroom for Python server runtime, OS kernel, and temporary buffers
    safety_margin = min(64.0, max(32.0, avail_mb * 0.10))  # 10% safety margin, bounded between 32MB and 64MB
    usable_mb = max(32.0, avail_mb - safety_margin)  # Calculate usable budget

    # Concurrency allocation bounded by both CPU quota and usable RAM
    # On fractional CPU containers (e.g. Render 0.1 CPU), running multiple workers
    # throttles the container, causing Python to drop HTTP pings and trigger 502 errors.
    if cpu_quota < 1.2 or usable_mb < 350.0:  # Fractional CPU or low memory
        workers = 1  # Exactly 1 worker prevents CPU starvation
        threads_per_worker = 1  # 1 thread
    elif cpu_quota < 2.2 or usable_mb < 850.0:  # Dual-core or moderate memory
        workers = 2  # 2 parallel workers
        threads_per_worker = 1  # 1 thread each
    elif cpu_quota < 4.2 or usable_mb < 1800.0:  # Quad-core or good memory
        workers = min(3, int(cpu_quota))  # Up to 3 workers
        threads_per_worker = 1  # 1 thread each
    else:  # High-resource machine (e.g. 8+ cores, > 1.8 GB RAM)
        workers = min(6, int(cpu_quota))  # Up to 6 parallel workers
        threads_per_worker = 2  # 2 threads each

    return RenderBudget(  # Return typed budget
        available_mb=round(avail_mb, 1),  # Measured available memory
        usable_mb=round(usable_mb, 1),  # Usable budget after safety margin
        workers=workers,  # Worker count
        threads_per_worker=threads_per_worker,  # Threads per worker
        safety_margin_mb=round(safety_margin, 1),  # Safety reserve
    )  # Budget instantiated
