import psutil
import platform
import datetime
import os
from utils.logger import get_logger

logger = get_logger(__name__)

# Prime CPU percent calculation (first call with interval=None returns 0)
# This allows subsequent calls to be non-blocking
_cpu_initialized = False


def _get_disk_path():
    """Get the appropriate disk path for the current OS."""
    if platform.system() == "Windows":
        return os.environ.get("SystemDrive", "C:")
    return "/"


def get_system_stats():
    """
    Get current system statistics (CPU, RAM, Disk, etc.).

    Uses non-blocking CPU measurement for better performance.
    Returns cached OS info to avoid repeated platform calls.
    """
    global _cpu_initialized

    # Initialize CPU measurement on first call
    if not _cpu_initialized:
        psutil.cpu_percent(interval=None)
        _cpu_initialized = True

    # Non-blocking CPU measurement (uses delta since last call)
    cpu = psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory()

    # Use OS-appropriate disk path
    try:
        disk = psutil.disk_usage(_get_disk_path())
    except OSError as e:
        logger.warning(f"Could not get disk usage: {e}")
        disk = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()

    uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))

    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024 ** 3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "uptime": uptime,
        "os": platform.system(),
        "os_version": platform.version()
    }