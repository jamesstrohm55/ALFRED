"""
System monitor command handler for A.L.F.R.E.D - processes system status queries.
"""
from __future__ import annotations

from typing import Optional

from services.system_monitor import get_system_stats, SystemStats
from ui.system_overlay import launch_system_overlay


def handle_system_monitor_command(user_input: str) -> Optional[str]:
    """
    Handle system monitoring commands.

    Args:
        user_input: The user's command text

    Returns:
        System status response or None if not a system command
    """
    user_input = user_input.lower()

    keywords: list[str] = [
        "system monitor",
        "system status",
        "how is the system",
        "system stats",
        "system information",
        "check systems"
    ]

    if any(word in user_input for word in keywords):
        stats: SystemStats = get_system_stats()

        response: str = (
            f"CPU Usage: {stats['cpu_percent']} percent. "
            f"RAM: {stats['ram_used_gb']} out of {stats['ram_total_gb']} gigabytes used "
            f"({stats['ram_percent']} percent). "
            f"Disk: {stats['disk_used_gb']} out of {stats['disk_total_gb']} gigabytes used "
            f"({stats['disk_percent']} percent). "
            f"Uptime: {stats['uptime']}. "
            f"OS: {stats['os']} {stats['os_version']}."
        )

        return response

    if "launch system overlay" in user_input or "show monitor" in user_input:
        launch_system_overlay()
        return "Launching system overlay..."

    return None