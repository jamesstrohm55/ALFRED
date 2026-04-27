"""
Date separator widget for grouping chat messages by time.
"""

from datetime import date, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class DateSeparator(QWidget):
    """Horizontal line with centered date label for message grouping."""

    def __init__(self, message_date: date, parent=None):
        super().__init__(parent)
        self._date = message_date
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)

        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setFixedHeight(1)
        left_line.setStyleSheet("background-color: rgba(0, 212, 255, 0.08); border: none;")

        date_label = QLabel(self._format_date().upper())
        date_label.setFont(QFont("Segoe UI", 7))
        date_label.setStyleSheet("color: rgba(0, 212, 255, 0.35); letter-spacing: 2px; background: transparent;")
        date_label.setAlignment(Qt.AlignCenter)

        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setFixedHeight(1)
        right_line.setStyleSheet("background-color: rgba(0, 212, 255, 0.08); border: none;")

        layout.addWidget(left_line, stretch=1)
        layout.addWidget(date_label)
        layout.addWidget(right_line, stretch=1)

    def _format_date(self) -> str:
        """Format the date as a human-readable string."""
        today = date.today()

        if self._date == today:
            return "Today"
        elif self._date == today - timedelta(days=1):
            return "Yesterday"
        elif self._date >= today - timedelta(days=7):
            return self._date.strftime("%A")  # Day name (e.g., "Monday")
        else:
            return self._date.strftime("%B %d, %Y")  # e.g., "March 10, 2026"
