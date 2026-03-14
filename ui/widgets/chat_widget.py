"""
Modern chat widget with message bubbles, markdown rendering, avatars, and animations.
"""

from datetime import date, datetime

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ui.styles.colors import COLORS
from ui.utils import load_svg_pixmap
from ui.widgets.date_separator import DateSeparator

try:
    import markdown

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def _create_circular_pixmap(pixmap: QPixmap, size: int) -> QPixmap:
    """Create a circular version of a pixmap."""
    if pixmap.isNull():
        return pixmap
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, scaled)
    painter.end()
    return result


def _render_markdown_html(text: str) -> str:
    """Convert markdown text to styled HTML for display in chat."""
    if not HAS_MARKDOWN:
        # Fallback: basic HTML escaping with line breaks
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return escaped.replace("\n", "<br>")

    html = markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br", "sane_lists"])

    styled = f"""
    <style>
        body {{
            color: {COLORS["text_primary"]};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            margin: 0;
            padding: 0;
        }}
        p {{ margin: 4px 0; }}
        code {{
            background-color: {COLORS["bg_primary"]};
            color: {COLORS["accent_cyan"]};
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 9pt;
        }}
        pre {{
            background-color: {COLORS["bg_primary"]};
            border: 1px solid {COLORS["border_default"]};
            border-radius: 6px;
            padding: 10px;
            margin: 6px 0;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        strong, b {{ color: {COLORS["text_primary"]}; }}
        em, i {{ color: {COLORS["text_secondary"]}; }}
        a {{ color: {COLORS["accent_cyan"]}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ margin: 4px 0; padding-left: 20px; }}
        li {{ margin: 2px 0; }}
        table {{
            border-collapse: collapse;
            margin: 6px 0;
        }}
        th, td {{
            border: 1px solid {COLORS["border_default"]};
            padding: 6px 10px;
            text-align: left;
        }}
        th {{
            background-color: {COLORS["bg_primary"]};
            color: {COLORS["accent_cyan"]};
        }}
        h1, h2, h3, h4 {{
            color: {COLORS["accent_cyan"]};
            margin: 8px 0 4px 0;
        }}
        blockquote {{
            border-left: 3px solid {COLORS["accent_cyan"]};
            margin: 6px 0;
            padding: 4px 12px;
            color: {COLORS["text_secondary"]};
        }}
    </style>
    <body>{html}</body>
    """
    return styled


class ChatBubble(QFrame):
    """Individual chat message bubble with avatar."""

    def __init__(self, sender: str, message: str, timestamp: datetime = None, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.is_user = sender.lower() in ("you", "user")
        self._setup_ui(message, timestamp)
        self._apply_style()

    def _setup_ui(self, message: str, timestamp: datetime):
        """Set up the bubble UI with avatar."""
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(10)

        # Avatar
        avatar_label = QLabel()
        avatar_label.setFixedSize(32, 32)
        avatar_label.setStyleSheet("background: transparent;")
        avatar_name = "user_avatar" if self.is_user else "alfred_avatar"
        avatar_pixmap = load_svg_pixmap(avatar_name, 32)
        if not avatar_pixmap.isNull():
            circular = _create_circular_pixmap(avatar_pixmap, 32)
            avatar_label.setPixmap(circular)
        else:
            avatar_label.setText("U" if self.is_user else "A")
            avatar_label.setAlignment(Qt.AlignCenter)
            color = COLORS["bubble_user"] if self.is_user else COLORS["accent_cyan"]
            avatar_label.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 12px;
            """)

        # Content area
        content_widget = QFrame()
        content_widget.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(4)

        # Sender label
        sender_label = QLabel(self.sender)
        sender_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        sender_label.setStyleSheet("background: transparent;")
        if self.is_user:
            sender_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
            sender_label.setAlignment(Qt.AlignRight)
        else:
            sender_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent;")
            sender_label.setAlignment(Qt.AlignLeft)

        # Message content
        if self.is_user:
            # Plain text for user messages
            self.message_label = QLabel(message)
            self.message_label.setWordWrap(True)
            self.message_label.setFont(QFont("Segoe UI", 10))
            self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            self.message_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        else:
            # Markdown-rendered HTML for ALFRED messages
            self.message_label = QTextBrowser()
            self.message_label.setOpenExternalLinks(True)
            self.message_label.setReadOnly(True)
            self.message_label.setFrameShape(QFrame.NoFrame)
            self.message_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.message_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.message_label.setStyleSheet(f"""
                QTextBrowser {{
                    background-color: transparent;
                    color: {COLORS["text_primary"]};
                    border: none;
                }}
            """)
            self.message_label.setHtml(_render_markdown_html(message))
            # Auto-size to content
            self.message_label.document().contentsChanged.connect(self._adjust_text_height)
            QTimer.singleShot(10, self._adjust_text_height)

        # Timestamp
        time_str = timestamp.strftime("%H:%M") if timestamp else datetime.now().strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Segoe UI", 7))
        time_label.setStyleSheet(f"color: {COLORS['text_disabled']}; background: transparent;")
        if self.is_user:
            time_label.setAlignment(Qt.AlignRight)
        else:
            time_label.setAlignment(Qt.AlignLeft)

        content_layout.addWidget(sender_label)
        content_layout.addWidget(self.message_label)
        content_layout.addWidget(time_label)

        # Arrange avatar and content based on sender
        if self.is_user:
            outer_layout.addStretch()
            outer_layout.addWidget(content_widget)
            outer_layout.addWidget(avatar_label, alignment=Qt.AlignTop)
        else:
            outer_layout.addWidget(avatar_label, alignment=Qt.AlignTop)
            outer_layout.addWidget(content_widget)
            outer_layout.addStretch()

    def _adjust_text_height(self):
        """Adjust QTextBrowser height to fit content."""
        if isinstance(self.message_label, QTextBrowser):
            doc_height = self.message_label.document().size().height()
            self.message_label.setFixedHeight(int(doc_height) + 4)

    def _apply_style(self):
        """Apply styling based on sender."""
        if self.is_user:
            self.setStyleSheet(f"""
                ChatBubble {{
                    background-color: {COLORS["bubble_user"]};
                    border-radius: 16px;
                    border-top-right-radius: 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                ChatBubble {{
                    background-color: {COLORS["bubble_alfred"]};
                    border-radius: 16px;
                    border-top-left-radius: 4px;
                    border: 1px solid {COLORS["border_default"]};
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
                background-color: {COLORS["bg_tertiary"]};
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
    """Scrollable chat history with message bubbles, date separators, and animations."""

    message_added = Signal(str, str)  # sender, content

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._messages = []
        self._last_message_date = None

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
                background-color: {COLORS["bg_secondary"]};
            }}
            QScrollBar:vertical {{
                background-color: {COLORS["scrollbar_bg"]};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS["scrollbar_handle"]};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS["scrollbar_hover"]};
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
        """Add a new message bubble to the chat with fade-in animation."""
        if timestamp is None:
            timestamp = datetime.now()

        # Insert date separator if needed
        msg_date = timestamp.date() if isinstance(timestamp, datetime) else date.today()
        if self._last_message_date is None or msg_date != self._last_message_date:
            separator = DateSeparator(msg_date)
            insert_index = self.layout.count() - 2
            self.layout.insertWidget(insert_index, separator)
            self._last_message_date = msg_date

        bubble = ChatBubble(sender, message, timestamp)

        # Set max width for bubble
        bubble.setMaximumWidth(int(self.width() * 0.75))
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        # Create wrapper for alignment
        wrapper = QWidget()
        wrapper.setStyleSheet("background-color: transparent;")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        is_user = sender.lower() in ("you", "user")
        if is_user:
            wrapper_layout.addStretch()
            wrapper_layout.addWidget(bubble)
        else:
            wrapper_layout.addWidget(bubble)
            wrapper_layout.addStretch()

        # Insert before the stretch and typing indicator
        insert_index = self.layout.count() - 2
        self.layout.insertWidget(insert_index, wrapper)

        self._messages.append((sender, message, timestamp))

        # Fade-in animation
        opacity_effect = QGraphicsOpacityEffect(wrapper)
        wrapper.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)

        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(300)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        fade_anim.start()
        # Store reference to prevent garbage collection
        wrapper._fade_anim = fade_anim

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
        while self.layout.count() > 2:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._messages = []
        self._last_message_date = None

    def get_message_count(self) -> int:
        """Get the number of messages."""
        return len(self._messages)

    def resizeEvent(self, event):
        """Handle resize to update bubble widths."""
        super().resizeEvent(event)
        for i in range(self.layout.count() - 2):
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
