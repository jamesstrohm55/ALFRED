"""
Input bar widget with text entry, send button, and microphone button.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QKeyEvent

from ui.styles.colors import COLORS


class InputBar(QWidget):
    """Text input bar with send and microphone buttons."""

    text_submitted = Signal(str)        # Emitted when user submits text
    voice_button_clicked = Signal()     # Emitted when mic button is clicked
    voice_button_released = Signal()    # Emitted when mic button is released

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_listening = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Microphone button
        self.mic_button = QPushButton()
        self.mic_button.setText("\U0001F3A4")  # Microphone emoji
        self.mic_button.setFixedSize(44, 44)
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.setToolTip("Click to speak (hold for continuous)")
        self._style_mic_button(False)

        # Text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setFont(QFont("Segoe UI", 11))
        self.text_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.text_input.setMinimumHeight(44)
        self._style_text_input()

        # Send button
        self.send_button = QPushButton()
        self.send_button.setText("\U0001F4E4")  # Outbox emoji
        self.send_button.setFixedSize(44, 44)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setToolTip("Send message")
        self._style_send_button()

        # Add widgets to layout
        layout.addWidget(self.mic_button)
        layout.addWidget(self.text_input)
        layout.addWidget(self.send_button)

    def _style_mic_button(self, is_listening: bool):
        """Style the microphone button based on listening state."""
        if is_listening:
            self.mic_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_red']};
                    border: none;
                    border-radius: 22px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: #ff6666;
                }}
            """)
        else:
            self.mic_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    border: 1px solid {COLORS['border_default']};
                    border-radius: 22px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    border-color: {COLORS['accent_cyan']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['accent_cyan']};
                }}
            """)

    def _style_text_input(self):
        """Style the text input field."""
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_default']};
                border-radius: 22px;
                padding: 0 16px;
                selection-background-color: {COLORS['accent_cyan']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_cyan']};
            }}
        """)

    def _style_send_button(self):
        """Style the send button."""
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_cyan']};
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_cyan_dim']};
            }}
            QPushButton:pressed {{
                background-color: #0077aa;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_tertiary']};
            }}
        """)

    def _connect_signals(self):
        """Connect internal signals."""
        self.send_button.clicked.connect(self._on_send_clicked)
        self.text_input.returnPressed.connect(self._on_send_clicked)
        self.mic_button.clicked.connect(self._on_mic_clicked)

    def _on_send_clicked(self):
        """Handle send button click or Enter key press."""
        text = self.text_input.text().strip()
        if text:
            self.text_input.clear()
            self.text_submitted.emit(text)

    def _on_mic_clicked(self):
        """Handle microphone button click - start listening."""
        # Don't toggle - just start listening each time
        # The audio thread will auto-stop when speech is recognized
        if not self._is_listening:
            self.voice_button_clicked.emit()

    def set_listening_state(self, is_listening: bool):
        """Update the listening state from external source."""
        self._is_listening = is_listening
        self._style_mic_button(is_listening)

    def set_enabled(self, enabled: bool):
        """Enable or disable the input bar."""
        self.text_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.mic_button.setEnabled(enabled)

    def set_placeholder(self, text: str):
        """Update the placeholder text."""
        self.text_input.setPlaceholderText(text)

    def focus_input(self):
        """Set focus to the text input."""
        self.text_input.setFocus()
