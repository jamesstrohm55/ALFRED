"""
Quick access row list for common ALFRED commands.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.styles.colors import COLORS
from ui.widgets.system_dashboard import _section_header

QUICK_ACTIONS = [
    {"id": "system_status", "name": "SYSTEM",   "icon": "📊", "command": "system status",         "tooltip": "Check system health"},
    {"id": "weather",       "name": "WEATHER",  "icon": "🌤", "command": "what's the weather",     "tooltip": "Get current weather"},
    {"id": "calendar",      "name": "CALENDAR", "icon": "📅", "command": "what's on my calendar",  "tooltip": "View upcoming events"},
    {"id": "time",          "name": "TIME",     "icon": "🕐", "command": "tell time",              "tooltip": "Get current time"},
    {"id": "vscode",        "name": "VS CODE",  "icon": "💻", "command": "open vs code",           "tooltip": "Launch VS Code"},
    {"id": "browser",       "name": "BROWSER",  "icon": "🌐", "command": "open browser",           "tooltip": "Open web browser"},
    {"id": "add_event",     "name": "ADD EVENT","icon": "➕", "command": "add event",              "tooltip": "Create calendar event"},
    {"id": "find_file",     "name": "FIND FILE","icon": "🔍", "command": "find file",              "tooltip": "Search for files"},
    {"id": "lock",          "name": "LOCK",     "icon": "🔒", "command": "lock computer",          "tooltip": "Lock workstation"},
    {"id": "music",         "name": "MUSIC",    "icon": "🎵", "command": "play music",             "tooltip": "Play music"},
]

_IDLE_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        border: none;
        border-left: 2px solid transparent;
        border-radius: 0px;
        text-align: left;
        padding: 5px 7px;
    }}
    QPushButton:hover {{
        background-color: rgba(0, 212, 255, 0.06);
        border-left: 2px solid {COLORS["accent_cyan"]};
    }}
"""

_ACTIVE_STYLE = f"""
    QPushButton {{
        background-color: rgba(0, 212, 255, 0.10);
        border: none;
        border-left: 2px solid {COLORS["accent_cyan"]};
        border-radius: 0px;
        text-align: left;
        padding: 5px 7px;
    }}
"""


class ActionRow(QPushButton):
    """Single quick-action row: icon + uppercase label."""

    action_clicked = Signal(str, str)  # action_id, command

    def __init__(self, action_data: dict, parent=None):
        super().__init__(parent)
        self._action_data = action_data
        self._setup_ui()
        self.clicked.connect(self._on_clicked)

    def _setup_ui(self):
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._action_data.get("tooltip", ""))
        self.setStyleSheet(_IDLE_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(7, 0, 7, 0)
        layout.setSpacing(7)

        icon_label = QLabel(self._action_data.get("icon", "?"))
        icon_label.setFont(QFont("Segoe UI Emoji", 11))
        icon_label.setStyleSheet("background: transparent;")
        icon_label.setFixedWidth(18)

        name_label = QLabel(self._action_data.get("name", ""))
        name_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        name_label.setStyleSheet("color: rgba(255,255,255,0.55); background: transparent; letter-spacing: 0.5px;")

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch()

    def _on_clicked(self):
        self.action_clicked.emit(
            self._action_data.get("id", ""),
            self._action_data.get("command", ""),
        )


class QuickActionsWidget(QWidget):
    """Vertical list of quick-access action rows."""

    action_triggered = Signal(str, str)  # action_id, command

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[ActionRow] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(2)

        layout.addWidget(_section_header("QUICK ACCESS"))

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(0, 212, 255, 0.10); border: none;")
        layout.addWidget(separator)

        for action in QUICK_ACTIONS:
            row = ActionRow(action)
            row.action_clicked.connect(self._on_action_clicked)
            self._rows.append(row)
            layout.addWidget(row)

    def _on_action_clicked(self, action_id: str, command: str):
        self.action_triggered.emit(action_id, command)

    def highlight_tile(self, action_id: str, highlight: bool):
        """Highlight or un-highlight a row (preserves API used by main_window.py)."""
        for row in self._rows:
            if row._action_data.get("id") == action_id:
                row.setStyleSheet(_ACTIVE_STYLE if highlight else _IDLE_STYLE)
                break

    def set_tile_enabled(self, action_id: str, enabled: bool):
        for row in self._rows:
            if row._action_data.get("id") == action_id:
                row.setEnabled(enabled)
                break
