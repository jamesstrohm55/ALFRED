from logging import root
import tkinter as tk
from services.system_monitor import get_system_stats

def launch_system_overlay():
    root = tk.Tk()
    root.title("A.L.F.R.E.D System Overlay Monitor")
    root.geometry("400x300")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    label = tk.Label(root, text="Loading system stats...", font=("Consolas", 10), justify="left")
    label.pack(padx=10, pady=10, anchor="w")

    def update_stats():
        stats = get_system_stats()
        output = (
            f"🧠 CPU: {stats['cpu_percent']}%\n"
            f"💾 RAM: {stats['ram_used_gb']} / {stats['ram_total_gb']} GB ({stats['ram_percent']}%)\n"
            f"📂 Disk: {stats['disk_used_gb']} / {stats['disk_total_gb']} GB ({stats['disk_percent']}%)\n"
            f"🕒 Uptime: {stats['uptime']}"
        )
        label.config(text=output)
        root.after(1000, update_stats)  # Update every second

    update_stats()
    root.mainloop()