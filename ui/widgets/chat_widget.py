"""
Modern chat widget with message bubbles for ALFRED.
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Slot, Qt, QTimer
from PySide6.QtGui import QFont

from ui.styles.colors import COLORS


class ChatBubble(QFrame):
    """Individual chat message bubble."""

    def __init__(self, sender: str, message: str, timestamp: datetime = None, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.is_user = sender.lower() in ("you", "user")

        self._setup_ui(message, timestamp)
        self._apply_style()

    def _setup_ui(self, message: str, timestamp: datetime):
        """Set up the bubble UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Sender label (small, above message)
        sender_label = QLabel(self.sender)
        sender_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        if self.is_user:
            sender_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            sender_label.setAlignment(Qt.AlignRight)
        else:
            sender_label.setStyleSheet(f"color: {COLORS['accent_cyan']};")
            sender_label.setAlignment(Qt.AlignLeft)

        # Message text
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 10))
        self.message_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.message_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        # Timestamp
        time_str = timestamp.strftime("%H:%M") if timestamp else datetime.now().strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Segoe UI", 7))
        time_label.setStyleSheet(f"color: {COLORS['text_disabled']};")
        if self.is_user:
            time_label.setAlignment(Qt.AlignRight)
        else:
            time_label.setAlignment(Qt.AlignLeft)

        layout.addWidget(sender_label)
        layout.addWidget(self.message_label)
        layout.addWidget(time_label)

    def _apply_style(self):
        """Apply styling based on sender."""
        if self.is_user:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bubble_user']};
                    border-radius: 16px;
                    border-top-right-radius: 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bubble_alfred']};
                    border-radius: 16px;
                    border-top-left-radius: 4px;
                    border: 1px solid {COLORS['border_default']};
                }}
            """)


class TypingIndicator(QFrame):
    """Animated typing indicator showing ALFRED is processing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dots = 0
        self._setup_ui()
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)

    def _setup_ui(self):
        """Set up the indicator UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        self.label = QLabel("A.L.F.R.E.D is thinking")
        self.label.setFont(QFont("Segoe UI", 9))
        self.label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        layout.addWidget(self.label)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 12px;
            }}
        """)

    def _animate(self):
        """Animate the dots."""
        self._dots = (self._dots + 1) % 4
        dots = "." * self._dots
        self.label.setText(f"A.L.F.R.E.D is thinking{dots}")

    def start(self):
        """Start the animation."""
        self._timer.start(400)
        self.show()

    def stop(self):
        """Stop the animation."""
        self._timer.stop()
        self.hide()


class ChatWidget(QScrollArea):
    """Scrollable chat history with message bubbles."""

    message_added = Signal(str, str)  # sender, content

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._messages = []

    def _setup_ui(self):
        """Initialize the chat widget."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignTop)

        # Typing indicator (hidden by default)
        self.typing_indicator = TypingIndicator()
        self.typing_indicator.hide()

        # Add stretch at the bottom to push messages up
        self.layout.addStretch()
        self.layout.addWidget(self.typing_indicator)

        self.setWidget(self.container)

        # Style the scroll area
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLORS['bg_secondary']};
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['scrollbar_bg']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['scrollbar_handle']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

    @Slot(str, str)
    def add_message(self, sender: str, message: str, timestamp: datetime = None):
        """Add a new message bubble to the chat."""
        bubble = ChatBubble(sender, message, timestamp)
        is_user = sender.lower() in ("you", "user")

        # Set max width for bubble
        bubble.setMaximumWidth(int(self.width() * 0.75))
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        # Create wrapper for alignment
        wrapper = QWidget()
        wrapper.setStyleSheet("background-color: transparent;")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        if is_user:
            wrapper_layout.addStretch()
            wrapper_layout.addWidget(bubble)
        else:
            wrapper_layout.addWidget(bubble)
            wrapper_layout.addStretch()

        # Insert before the stretch and typing indicator
        insert_index = self.layout.count() - 2  # Before stretch and typing indicator
        self.layout.insertWidget(insert_index, wrapper)

        self._messages.append((sender, message, timestamp))

        # Auto-scroll to bottom
        QTimer.singleShot(50, self._scroll_to_bottom)

        # Emit signal
        self.message_added.emit(sender, message)

    def show_typing(self):
        """Show the typing indicator."""
        self.typing_indicator.start()
        QTimer.singleShot(50, self._scroll_to_bottom)

    def hide_typing(self):
        """Hide the typing indicator."""
        self.typing_indicator.stop()

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_messages(self):
        """Clear all messages from the chat."""
        # Remove all widgets except the stretch and typing indicator
        while self.layout.count() > 2:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._messages = []

    def get_message_count(self) -> int:
        """Get the number of messages."""
        return len(self._messages)

    def resizeEvent(self, event):
        """Handle resize to update bubble widths."""
        super().resizeEvent(event)
        # Update max widths of existing bubbles
        for i in range(self.layout.count() - 2):  # Exclude stretch and typing indicator
            item = self.layout.itemAt(i)
            if item and item.widget():
                wrapper = item.widget()
                wrapper_layout = wrapper.layout()
                if wrapper_layout:
                    for j in range(wrapper_layout.count()):
                        bubble_item = wrapper_layout.itemAt(j)
                        if bubble_item and bubble_item.widget():
                            widget = bubble_item.widget()
                            if isinstance(widget, ChatBubble):
                                widget.setMaximumWidth(int(self.width() * 0.75))
