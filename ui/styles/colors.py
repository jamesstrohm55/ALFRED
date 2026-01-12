"""
JARVIS-inspired dark theme color palette for ALFRED GUI.
"""

COLORS = {
    # Backgrounds
    'bg_primary': '#0a0a14',        # Deepest background
    'bg_secondary': '#1a1a2e',      # Card/panel background
    'bg_tertiary': '#2d2d44',       # Elevated elements
    'bg_hover': '#3d3d54',          # Hover state
    'bg_pressed': '#4d4d64',        # Pressed/active state

    # Accents
    'accent_cyan': '#00d4ff',       # Primary accent (JARVIS blue)
    'accent_cyan_dim': '#0099cc',   # Dimmed cyan
    'accent_green': '#00ff88',      # Success/RAM indicator
    'accent_green_dim': '#00cc66',  # Dimmed green
    'accent_orange': '#ff8800',     # Warning/Disk indicator
    'accent_red': '#ff4444',        # Error/Critical
    'accent_purple': '#aa88ff',     # Secondary accent

    # Text
    'text_primary': '#ffffff',      # Primary text
    'text_secondary': '#aaaaaa',    # Secondary/muted text
    'text_disabled': '#666666',     # Disabled text
    'text_highlight': '#00d4ff',    # Highlighted text

    # Borders
    'border_default': '#333344',    # Default border
    'border_focus': '#00d4ff',      # Focused border
    'border_hover': '#444466',      # Hover border

    # Chat bubbles
    'bubble_user': '#0066cc',       # User message background
    'bubble_alfred': '#2d2d44',     # ALFRED message background

    # Waveform
    'waveform_input': '#00d4ff',    # Input waveform color (cyan)
    'waveform_output': '#00ff88',   # Output waveform color (green)
    'waveform_bg': '#1a1a2e',       # Waveform background

    # Charts
    'chart_cpu': '#00d4ff',         # CPU chart line
    'chart_ram': '#00ff88',         # RAM chart line
    'chart_disk': '#ff8800',        # Disk chart line
    'chart_grid': '#333344',        # Chart grid lines

    # Progress bars
    'progress_bg': '#1a1a2e',       # Progress bar background
    'progress_chunk': '#00d4ff',    # Progress bar fill

    # Scrollbar
    'scrollbar_bg': '#1a1a2e',      # Scrollbar background
    'scrollbar_handle': '#444466',  # Scrollbar handle
    'scrollbar_hover': '#555577',   # Scrollbar handle hover
}


def get_color(name: str) -> str:
    """Get a color by name, with fallback to white."""
    return COLORS.get(name, '#ffffff')


def rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string with given alpha (0.0-1.0)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'
