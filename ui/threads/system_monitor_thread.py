"""
System monitor thread for polling system statistics.
"""
from PySide6.QtCore import QThread, Signal


class SystemMonitorThread(QThread):
    """Thread that polls system statistics at regular intervals."""

    stats_updated = Signal(dict)  # Emits system stats dictionary

    def __init__(self, interval_ms: int = 1000, parent=None):
        """
        Initialize the system monitor thread.

        Args:
            interval_ms: Polling interval in milliseconds (default: 1000ms)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._interval = interval_ms
        self._running = True

    def run(self):
        """Main thread loop that polls system statistics."""
        # Import here to avoid circular imports
        from services.system_monitor import get_system_stats

        while self._running:
            try:
                stats = get_system_stats()
                self.stats_updated.emit(stats)
            except Exception as e:
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
