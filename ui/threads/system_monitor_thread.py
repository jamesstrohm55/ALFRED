"""
System monitor thread for polling system statistics.
"""
from PySide6.QtCore import QThread, Signal
from utils.logger import get_logger

logger = get_logger(__name__)

# Default polling interval - 2 seconds is sufficient for UI updates
# and reduces CPU overhead compared to 1 second polling
DEFAULT_INTERVAL_MS = 2000


class SystemMonitorThread(QThread):
    """Thread that polls system statistics at regular intervals."""

    stats_updated = Signal(dict)  # Emits system stats dictionary

    def __init__(self, interval_ms: int = DEFAULT_INTERVAL_MS, parent=None):
        """
        Initialize the system monitor thread.

        Args:
            interval_ms: Polling interval in milliseconds (default: 2000ms)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._interval = interval_ms
        self._running = True
        self._error_count = 0
        self._max_consecutive_errors = 5

    def run(self):
        """Main thread loop that polls system statistics."""
        # Import here to avoid circular imports
        from services.system_monitor import get_system_stats

        logger.debug(f"System monitor started with {self._interval}ms interval")

        while self._running:
            try:
                stats = get_system_stats()
                self.stats_updated.emit(stats)
                self._error_count = 0  # Reset on success

            except Exception as e:
                self._error_count += 1
                logger.warning(f"System stats error ({self._error_count}): {e}")

                # Emit error stats on failure
                self.stats_updated.emit({
                    'cpu_percent': 0,
                    'ram_percent': 0,
                    'ram_used_gb': 0,
                    'ram_total_gb': 0,
                    'disk_percent': 0,
                    'disk_used_gb': 0,
                    'disk_total_gb': 0,
                    'uptime': 'Error',
                    'os': 'Unknown',
                    'os_version': '',
                    'error': str(e)
                })

                # Back off if too many consecutive errors
                if self._error_count >= self._max_consecutive_errors:
                    logger.error("Too many consecutive errors, increasing poll interval")
                    self._interval = min(self._interval * 2, 10000)  # Max 10 seconds

            # Sleep for the interval
            self.msleep(self._interval)

    def stop(self):
        """Stop the monitoring thread."""
        self._running = False
        self.wait()

    def set_interval(self, interval_ms: int):
        """
        Set the polling interval.

        Args:
            interval_ms: New polling interval in milliseconds
        """
        self._interval = max(100, interval_ms)  # Minimum 100ms
