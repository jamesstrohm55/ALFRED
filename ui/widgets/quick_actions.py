"""
Quick action tiles widget with SVG icons for common ALFRED commands.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.styles.colors import COLORS
from ui.utils import load_svg_pixmap

# Quick action definitions with SVG icon names
QUICK_ACTIONS = [
    {
        "id": "system_status",
        "name": "System",
        "icon": "\U0001f4ca",
        "icon_svg": "system",
        "command": "system status",
        "tooltip": "Check system health",
    },
    {
        "id": "weather",
        "name": "Weather",
        "icon": "\U0001f324",
        "icon_svg": "weather",
        "command": "what's the weather",
        "tooltip": "Get current weather",
    },
    {
        "id": "calendar",
        "name": "Calendar",
        "icon": "\U0001f4c5",
        "icon_svg": "calendar",
        "command": "what's on my calendar",
        "tooltip": "View upcoming events",
    },
    {
        "id": "time",
        "name": "Time",
        "icon": "\U0001f551",
        "icon_svg": "time",
        "command": "tell time",
        "tooltip": "Get current time",
    },
    {
        "id": "vscode",
        "name": "VS Code",
        "icon": "\U0001f4bb",
        "icon_svg": "vscode",
        "command": "open vs code",
        "tooltip": "Launch VS Code",
    },
    {
        "id": "browser",
        "name": "Browser",
        "icon": "\U0001f310",
        "icon_svg": "browser",
        "command": "open browser",
        "tooltip": "Open web browser",
    },
    {
        "id": "add_event",
        "name": "Add Event",
        "icon": "\U00002795",
        "icon_svg": "add_event",
        "command": "add event",
        "tooltip": "Create calendar event",
    },
    {
        "id": "find_file",
        "name": "Find File",
        "icon": "\U0001f50d",
        "icon_svg": "find_file",
        "command": "find file",
        "tooltip": "Search for files",
    },
    {
        "id": "lock",
        "name": "Lock",
        "icon": "\U0001f512",
        "icon_svg": "lock",
        "command": "lock computer",
        "tooltip": "Lock workstation",
    },
    {
        "id": "music",
        "name": "Music",
        "icon": "\U0001f3b5",
        "icon_svg": "music",
        "command": "play music",
        "tooltip": "Play music",
    },
]


class ActionTile(QPushButton):
    """Individual quick action tile button with SVG icon."""

    action_clicked = Signal(str, str)  # action_id, command

    def __init__(self, action_data: dict, parent=None):
        super().__init__(parent)
        self._action_data = action_data
        self._setup_ui()
        self.clicked.connect(self._on_clicked)

    def _setup_ui(self):
        """Set up the tile UI with SVG icon or emoji fallback."""
        self.setFixedSize(80, 80)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._action_data.get("tooltip", ""))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Try SVG icon first, fall back to emoji
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        svg_name = self._action_data.get("icon_svg", "")
        if svg_name:
            pixmap = load_svg_pixmap(svg_name, 28)
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap)
            else:
                # Fallback to emoji
                icon_label.setText(self._action_data.get("icon", "\U00002753"))
                icon_label.setFont(QFont("Segoe UI Emoji", 24))
        else:
            icon_label.setText(self._action_data.get("icon", "\U00002753"))
            icon_label.setFont(QFont("Segoe UI Emoji", 24))

        # Name label
        name_label = QLabel(self._action_data.get("name", "Action"))
        name_label.setFont(QFont("Segoe UI", 8))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        name_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        # Styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                border: 2px solid transparent;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_hover"]};
                border-color: {COLORS["border_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {COLORS["bg_pressed"]};
                border-color: {COLORS["accent_cyan"]};
            }}
        """)

    def _on_clicked(self):
        """Handle tile click."""
        self.action_clicked.emit(self._action_data.get("id", ""), self._action_data.get("command", ""))


class QuickActionsWidget(QWidget):
    """Grid of quick action tiles."""

    action_triggered = Signal(str, str)  # action_id, command

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tiles = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the quick actions grid."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Title
        title = QLabel("QUICK ACTIONS")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet(f"""
            color: {COLORS["accent_cyan"]};
            padding: 8px;
            background-color: {COLORS["bg_secondary"]};
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Grid container
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_secondary"]};
                border-radius: 8px;
                border: 1px solid {COLORS["border_default"]};
            }}
        """)

        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(12, 12, 12, 12)
        grid_layout.setSpacing(8)

        # Create action tiles in a 5x2 grid
        for i, action in enumerate(QUICK_ACTIONS):
            row = i // 5
            col = i % 5

            tile = ActionTile(action)
            tile.action_clicked.connect(self._on_action_clicked)
            self._tiles.append(tile)

            grid_layout.addWidget(tile, row, col)

        main_layout.addWidget(title)
        main_layout.addWidget(grid_frame)

    def _on_action_clicked(self, action_id: str, command: str):
        """Handle action tile click."""
        self.action_triggered.emit(action_id, command)

    def set_tile_enabled(self, action_id: str, enabled: bool):
        """Enable or disable a specific tile."""
        for tile in self._tiles:
            if tile._action_data.get("id") == action_id:
                tile.setEnabled(enabled)
                break

    def highlight_tile(self, action_id: str, highlight: bool):
        """Highlight a specific tile."""
        for tile in self._tiles:
            if tile._action_data.get("id") == action_id:
                if highlight:
                    tile.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS["bg_hover"]};
                            border: 2px solid {COLORS["accent_cyan"]};
                            border-radius: 12px;
                        }}
                    """)
                else:
                    tile.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS["bg_tertiary"]};
                            border: 2px solid transparent;
                            border-radius: 12px;
                        }}
                        QPushButton:hover {{
                            background-color: {COLORS["bg_hover"]};
                            border-color: {COLORS["border_hover"]};
                        }}
                        QPushButton:pressed {{
                            background-color: {COLORS["bg_pressed"]};
                            border-color: {COLORS["accent_cyan"]};
                        }}
                    """)
                break
