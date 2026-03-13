"""
Collapsible sidebar widget for ALFRED.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSizePolicy, QFrame
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont

from ui.styles.colors import COLORS
from ui.utils import load_svg_icon


class CollapsibleSidebar(QWidget):
    """Sidebar that can collapse/expand with smooth animation."""

    toggled = Signal(bool)  # Emitted with is_expanded state

    EXPANDED_WIDTH = 350
    COLLAPSED_WIDTH = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_expanded = True
        self._content_widget = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the sidebar layout."""
        self.setMinimumWidth(0)
        self.setMaximumWidth(self.EXPANDED_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle button bar
        toggle_bar = QWidget()
        toggle_bar.setFixedHeight(36)
        toggle_bar.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        toggle_layout = QVBoxLayout(toggle_bar)
        toggle_layout.setContentsMargins(4, 4, 4, 4)

        self.toggle_btn = QPushButton()
        collapse_icon = load_svg_icon("collapse", 16)
        if not collapse_icon.isNull():
            self.toggle_btn.setIcon(collapse_icon)
        else:
            self.toggle_btn.setText("\u00AB")  # «
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setToolTip("Toggle sidebar (Ctrl+B)")
        self.toggle_btn.clicked.connect(self.toggle)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['accent_cyan']};
            }}
        """)

        toggle_layout.addWidget(self.toggle_btn, alignment=Qt.AlignRight)

        # Content area (dashboard + quick actions will be added here)
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)

        layout.addWidget(toggle_bar)
        layout.addWidget(self._content_widget, stretch=1)

        # Animation
        self._animation = QPropertyAnimation(self, b"maximumWidth")
        self._animation.setDuration(250)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

    def add_widget(self, widget: QWidget):
        """Add a widget to the sidebar content area."""
        self._content_layout.addWidget(widget)

    def add_stretch(self):
        """Add stretch to content layout."""
        self._content_layout.addStretch()

    def toggle(self):
        """Toggle between expanded and collapsed states."""
        self._is_expanded = not self._is_expanded

        self._animation.stop()

        if self._is_expanded:
            self._animation.setStartValue(self.width())
            self._animation.setEndValue(self.EXPANDED_WIDTH)
            self._content_widget.show()
            expand_icon = load_svg_icon("collapse", 16)
            if not expand_icon.isNull():
                self.toggle_btn.setIcon(expand_icon)
            else:
                self.toggle_btn.setText("\u00AB")
        else:
            self._animation.setStartValue(self.width())
            self._animation.setEndValue(self.COLLAPSED_WIDTH)
            collapse_icon = load_svg_icon("expand", 16)
            if not collapse_icon.isNull():
                self.toggle_btn.setIcon(collapse_icon)
            else:
                self.toggle_btn.setText("\u00BB")

        self._animation.start()

        # Hide content after collapse animation
        if not self._is_expanded:
            self._animation.finished.connect(self._on_collapsed)

        self.toggled.emit(self._is_expanded)

    def _on_collapsed(self):
        """Called when collapse animation finishes."""
        if not self._is_expanded:
            self._content_widget.hide()
        # Disconnect to avoid repeated calls
        try:
            self._animation.finished.disconnect(self._on_collapsed)
        except RuntimeError:
            pass

    @property
    def is_expanded(self) -> bool:
        """Whether the sidebar is currently expanded."""
        return self._is_expanded
