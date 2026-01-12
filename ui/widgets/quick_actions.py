"""
Quick action tiles widget for common ALFRED commands.
"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from ui.styles.colors import COLORS


# Quick action definitions
QUICK_ACTIONS = [
    {
        "id": "system_status",
        "name": "System",
        "icon": "\U0001F4CA",  # Chart emoji
        "command": "system status",
        "tooltip": "Check system health"
    },
    {
        "id": "weather",
        "name": "Weather",
        "icon": "\U0001F324",  # Sun behind cloud
        "command": "what's the weather",
        "tooltip": "Get current weather"
    },
    {
        "id": "calendar",
        "name": "Calendar",
        "icon": "\U0001F4C5",  # Calendar emoji
        "command": "what's on my calendar",
        "tooltip": "View upcoming events"
    },
    {
        "id": "time",
        "name": "Time",
        "icon": "\U0001F551",  # Clock emoji
        "command": "tell time",
        "tooltip": "Get current time"
    },
    {
        "id": "vscode",
        "name": "VS Code",
        "icon": "\U0001F4BB",  # Computer emoji
        "command": "open vs code",
        "tooltip": "Launch VS Code"
    },
    {
        "id": "browser",
        "name": "Browser",
        "icon": "\U0001F310",  # Globe emoji
        "command": "open browser",
        "tooltip": "Open web browser"
    },
    {
        "id": "add_event",
        "name": "Add Event",
        "icon": "\U00002795",  # Plus sign
        "command": "add event",
        "tooltip": "Create calendar event"
    },
    {
        "id": "find_file",
        "name": "Find File",
        "icon": "\U0001F50D",  # Magnifying glass
        "command": "find file",
        "tooltip": "Search for files"
    },
    {
        "id": "lock",
        "name": "Lock",
        "icon": "\U0001F512",  # Lock emoji
        "command": "lock computer",
        "tooltip": "Lock workstation"
    },
    {
        "id": "music",
        "name": "Music",
        "icon": "\U0001F3B5",  # Musical note
        "command": "play music",
        "tooltip": "Play music"
    },
]


class ActionTile(QPushButton):
    """Individual quick action tile button."""

    action_clicked = Signal(str, str)  # action_id, command

    def __init__(self, action_data: dict, parent=None):
        super().__init__(parent)
        self._action_data = action_data
        self._setup_ui()
        self.clicked.connect(self._on_clicked)

    def _setup_ui(self):
        """Set up the tile UI."""
        self.setFixedSize(80, 80)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._action_data.get('tooltip', ''))

        # Create layout for icon and label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Icon label
        icon_label = QLabel(self._action_data.get('icon', '\U00002753'))
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        # Name label
        name_label = QLabel(self._action_data.get('name', 'Action'))
        name_label.setFont(QFont("Segoe UI", 8))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        name_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        # Styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                border: 2px solid transparent;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_pressed']};
                border-color: {COLORS['accent_cyan']};
            }}
        """)

    def _on_clicked(self):
        """Handle tile click."""
        self.action_clicked.emit(
            self._action_data.get('id', ''),
            self._action_data.get('command', '')
        )


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
            color: {COLORS['accent_cyan']};
            padding: 8px;
            background-color: {COLORS['bg_secondary']};
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Grid container
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border_default']};
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
            if tile._action_data.get('id') == action_id:
                tile.setEnabled(enabled)
                break

    def highlight_tile(self, action_id: str, highlight: bool):
        """Highlight a specific tile."""
        for tile in self._tiles:
            if tile._action_data.get('id') == action_id:
                if highlight:
                    tile.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['bg_hover']};
                            border: 2px solid {COLORS['accent_cyan']};
                            border-radius: 12px;
                        }}
                    """)
                else:
                    tile.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['bg_tertiary']};
                            border: 2px solid transparent;
                            border-radius: 12px;
                        }}
                        QPushButton:hover {{
                            background-color: {COLORS['bg_hover']};
                            border-color: {COLORS['border_hover']};
                        }}
                        QPushButton:pressed {{
                            background-color: {COLORS['bg_pressed']};
                            border-color: {COLORS['accent_cyan']};
                        }}
                    """)
                break
