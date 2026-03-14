"""
Status bar widget showing connection state, mic status, and model info.
"""

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from ui.styles.colors import COLORS


class StatusDot(QLabel):
    """Small colored status indicator dot."""

    def __init__(self, color: str = None, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.set_color(color or COLORS["accent_green"])

    def set_color(self, color: str):
        """Update the dot color."""
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 5px;
                border: none;
            }}
        """)


class StatusBar(QWidget):
    """Bottom status bar showing system state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the status bar layout."""
        self.setFixedHeight(28)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["bg_secondary"]};
                border-top: 1px solid {COLORS["border_default"]};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        font = QFont("Segoe UI", 8)

        # LLM Status
        self.llm_dot = StatusDot(COLORS["text_disabled"])
        self.llm_label = QLabel("LLM: Connecting...")
        self.llm_label.setFont(font)
        self.llm_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        # Separator
        sep1 = self._create_separator()

        # Mic Status
        self.mic_dot = StatusDot(COLORS["text_disabled"])
        self.mic_label = QLabel("Mic: Ready")
        self.mic_label.setFont(font)
        self.mic_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        # Separator
        sep2 = self._create_separator()

        # Voice Status
        self.voice_dot = StatusDot(COLORS["text_disabled"])
        self.voice_label = QLabel("Voice: Idle")
        self.voice_label.setFont(font)
        self.voice_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        # Add to layout
        layout.addWidget(self.llm_dot)
        layout.addWidget(self.llm_label)
        layout.addWidget(sep1)
        layout.addWidget(self.mic_dot)
        layout.addWidget(self.mic_label)
        layout.addWidget(sep2)
        layout.addWidget(self.voice_dot)
        layout.addWidget(self.voice_label)
        layout.addStretch()

    def _create_separator(self) -> QFrame:
        """Create a vertical separator line."""
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(16)
        sep.setStyleSheet(f"color: {COLORS['border_default']}; background: transparent;")
        return sep

    @Slot(str, bool)
    def set_llm_status(self, model_name: str, is_connected: bool):
        """Update LLM connection status."""
        if is_connected:
            self.llm_dot.set_color(COLORS["accent_green"])
            self.llm_label.setText(f"LLM: {model_name}")
        else:
            self.llm_dot.set_color(COLORS["accent_red"])
            self.llm_label.setText("LLM: Disconnected")

    @Slot(bool)
    def set_mic_status(self, is_listening: bool):
        """Update microphone status."""
        if is_listening:
            self.mic_dot.set_color(COLORS["accent_red"])
            self.mic_label.setText("Mic: Listening...")
        else:
            self.mic_dot.set_color(COLORS["accent_green"])
            self.mic_label.setText("Mic: Ready")

    @Slot(bool)
    def set_speaking(self, is_speaking: bool):
        """Update voice/TTS status."""
        if is_speaking:
            self.voice_dot.set_color(COLORS["accent_cyan"])
            self.voice_label.setText("Voice: Speaking...")
        else:
            self.voice_dot.set_color(COLORS["text_disabled"])
            self.voice_label.setText("Voice: Idle")
