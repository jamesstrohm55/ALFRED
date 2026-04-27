"""
Custom QPainter-based gradient progress bar.
Qt's QProgressBar ignores gradient fills on Windows — this replaces it.
"""

from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QWidget


class GradientBar(QWidget):
    """Thin horizontal bar with a left-to-right gradient fill."""

    def __init__(self, primary_hex: str, dim_hex: str, parent=None):
        super().__init__(parent)
        self._value = 0
        self._primary = QColor(primary_hex)
        self._dim = QColor(dim_hex)
        bg = QColor(primary_hex)
        bg.setAlpha(20)
        self._bg = bg
        self.setFixedHeight(3)
        self.setMinimumWidth(20)

    def set_value(self, value: int) -> None:
        self._value = max(0, min(100, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        painter.fillRect(0, 0, w, h, self._bg)

        fill_w = int(w * self._value / 100)
        if fill_w > 0:
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, self._primary)
            grad.setColorAt(1.0, self._dim)
            painter.fillRect(0, 0, fill_w, h, QBrush(grad))
