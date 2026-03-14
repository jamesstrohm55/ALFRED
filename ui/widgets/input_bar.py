"""
Input bar widget with text entry, send button, microphone button, and command history.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QWidget

from ui.styles.colors import COLORS
from ui.utils import load_svg_icon


class HistoryLineEdit(QLineEdit):
    """QLineEdit with up/down arrow key history navigation."""

    history_up = Signal()
    history_down = Signal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.history_up.emit()
        elif event.key() == Qt.Key_Down:
            self.history_down.emit()
        else:
            super().keyPressEvent(event)


class InputBar(QWidget):
    """Text input bar with send and microphone buttons and command history."""

    text_submitted = Signal(str)  # Emitted when user submits text
    voice_button_clicked = Signal()  # Emitted when mic button is clicked
    voice_button_released = Signal()  # Emitted when mic button is released

    MAX_HISTORY = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_listening = False
        self._history = []
        self._history_index = -1
        self._current_text = ""
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Microphone button
        self.mic_button = QPushButton()
        mic_icon = load_svg_icon("mic", 20)
        if not mic_icon.isNull():
            self.mic_button.setIcon(mic_icon)
            self.mic_button.setIconSize(QSize(20, 20))
        else:
            self.mic_button.setText("\U0001f3a4")
        self.mic_button.setFixedSize(44, 44)
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.setToolTip("Click to speak (hold for continuous)")
        self._style_mic_button(False)

        # Text input field with history support
        self.text_input = HistoryLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setFont(QFont("Segoe UI", 11))
        self.text_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.text_input.setMinimumHeight(44)
        self._style_text_input()

        # Send button
        self.send_button = QPushButton()
        send_icon = load_svg_icon("send", 20)
        if not send_icon.isNull():
            self.send_button.setIcon(send_icon)
            self.send_button.setIconSize(QSize(20, 20))
        else:
            self.send_button.setText("\U0001f4e4")
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
                    background-color: {COLORS["accent_red"]};
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
                    background-color: {COLORS["bg_tertiary"]};
                    border: 1px solid {COLORS["border_default"]};
                    border-radius: 22px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS["bg_hover"]};
                    border-color: {COLORS["accent_cyan"]};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS["accent_cyan"]};
                }}
            """)

    def _style_text_input(self):
        """Style the text input field."""
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["bg_secondary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border_default"]};
                border-radius: 22px;
                padding: 0 16px;
                selection-background-color: {COLORS["accent_cyan"]};
            }}
            QLineEdit:focus {{
                border-color: {COLORS["accent_cyan"]};
            }}
        """)

    def _style_send_button(self):
        """Style the send button."""
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent_cyan"]};
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_cyan_dim"]};
            }}
            QPushButton:pressed {{
                background-color: #0077aa;
            }}
            QPushButton:disabled {{
                background-color: {COLORS["bg_tertiary"]};
            }}
        """)

    def _connect_signals(self):
        """Connect internal signals."""
        self.send_button.clicked.connect(self._on_send_clicked)
        self.text_input.returnPressed.connect(self._on_send_clicked)
        self.mic_button.clicked.connect(self._on_mic_clicked)
        self.text_input.history_up.connect(self._on_history_up)
        self.text_input.history_down.connect(self._on_history_down)

    def _on_send_clicked(self):
        """Handle send button click or Enter key press."""
        text = self.text_input.text().strip()
        if text:
            # Add to history
            if not self._history or self._history[-1] != text:
                self._history.append(text)
                if len(self._history) > self.MAX_HISTORY:
                    self._history.pop(0)
            self._history_index = -1
            self._current_text = ""

            self.text_input.clear()
            self.text_submitted.emit(text)

    def _on_mic_clicked(self):
        """Handle microphone button click - start listening."""
        if not self._is_listening:
            self.voice_button_clicked.emit()

    def _on_history_up(self):
        """Navigate to previous command in history."""
        if not self._history:
            return

        if self._history_index == -1:
            # Save current text before navigating
            self._current_text = self.text_input.text()
            self._history_index = len(self._history) - 1
        elif self._history_index > 0:
            self._history_index -= 1

        self.text_input.setText(self._history[self._history_index])

    def _on_history_down(self):
        """Navigate to next command in history."""
        if self._history_index == -1:
            return

        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.text_input.setText(self._history[self._history_index])
        else:
            # Restore original text
            self._history_index = -1
            self.text_input.setText(self._current_text)

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
