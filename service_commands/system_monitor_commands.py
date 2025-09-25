from services.system_monitor import get_system_stats
from ui.system_overlay import launch_system_overlay


def handle_system_monitor_command(user_input):
    user_input = user_input.lower()

    keywords = [
        "system monitor",
        "system status",
        "how is the system",
        "system stats",
        "system information",
        "check systems"
    ]

    if any(word in user_input for word in keywords):
        stats = get_system_stats()

        response = (
            f"🧠 CPU Usage: {stats['cpu_percent']} percent. "
            f"💾 RAM: {stats['ram_used_gb']} out of {stats['ram_total_gb']} gigabytes used "
            f"({stats['ram_percent']} percent). "
            f"📂 Disk: {stats['disk_used_gb']} out of {stats['disk_total_gb']} gigabytes used "
            f"({stats['disk_percent']} percent). "
            f"🕒 Uptime: {stats['uptime']}. "
            f"🖥️ OS: {stats['os']} {stats['os_version']}."
        )

        return response

    if "launch system overlay" in user_input or "show monitor" in user_input:
        launch_system_overlay()
        return "Launching system overlay..."

    return None