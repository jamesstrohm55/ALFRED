"""
JARVIS-inspired dark theme color palette for ALFRED GUI.
"""

COLORS = {
    # Backgrounds
    "bg_primary": "#080812",  # was #0a0a14 — deeper
    "bg_secondary": "#111122",  # was #1a1a2e
    "bg_tertiary": "#1e1e32",  # was #2d2d44
    "bg_hover": "#2a2a3e",  # was #3d3d54
    "bg_pressed": "#363650",  # was #4d4d64
    "bg_sidebar": "#0a0a18",  # NEW — slightly darker than primary for depth
    # Accents
    "accent_cyan": "#00d4ff",
    "accent_cyan_dim": "#0088bb",  # was #0099cc — also doubles as secondary info cyan
    "accent_cyan_secondary": "#0088bb",  # NEW — alias, informational uses
    "accent_green": "#00cc66",  # was #00ff88 — less saturated, more refined
    "accent_green_dim": "#009944",  # was #00cc66
    "accent_orange": "#ff8800",
    "accent_red": "#ff4444",
    "accent_purple": "#aa88ff",
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#aaaaaa",
    "text_disabled": "#555566",  # was #666666 — slightly cooler
    "text_highlight": "#00d4ff",
    # Borders
    "border_default": "#1e1e32",  # was #333344 — subtler
    "border_focus": "#00d4ff",
    "border_hover": "#2a2a48",  # was #444466
    # Chat bubbles
    "bubble_user": "#0066cc",
    "bubble_alfred": "#1e1e32",
    "bubble_alfred_bg": "rgba(0, 212, 255, 0.05)",  # NEW
    "bubble_alfred_border": "rgba(0, 212, 255, 0.15)",  # NEW
    "bubble_user_bg": "rgba(0, 102, 204, 0.35)",  # NEW
    "bubble_user_border": "rgba(0, 136, 255, 0.30)",  # NEW
    # Waveform
    "waveform_input": "#00d4ff",
    "waveform_output": "#00cc66",
    "waveform_bg": "#111122",  # updated to match bg_secondary
    # Charts
    "chart_cpu": "#00d4ff",
    "chart_ram": "#00cc66",  # updated to match new green
    "chart_disk": "#ff8800",
    "chart_grid": "#1e1e32",  # updated
    # Progress bars
    "progress_bg": "#111122",
    "progress_chunk": "#00d4ff",
    # Scrollbar
    "scrollbar_bg": "#111122",
    "scrollbar_handle": "#2a2a48",
    "scrollbar_hover": "#363660",
}


def get_color(name: str) -> str:
    """Get a color by name, with fallback to white."""
    return COLORS.get(name, "#ffffff")


def rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string with given alpha (0.0-1.0)."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
