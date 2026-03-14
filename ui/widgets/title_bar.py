"""
Custom frameless title bar for ALFRED main window.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ui.styles.colors import COLORS
from ui.utils import load_svg_icon


class CustomTitleBar(QWidget):
    """Custom draggable title bar with minimize, maximize, and close buttons."""

    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._is_maximized = False
        self._setup_ui()
        self.setFixedHeight(40)

    def _setup_ui(self):
        """Set up the title bar layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        # ALFRED icon/logo
        logo_label = QLabel("\u25c6")  # Diamond character
        logo_label.setFont(QFont("Segoe UI", 14))
        logo_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent;")

        # Title
        title_label = QLabel("A.L.F.R.E.D")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent;")

        # Version label
        version_label = QLabel("v2.0")
        version_label.setFont(QFont("Segoe UI", 8))
        version_label.setStyleSheet(f"color: {COLORS['text_disabled']}; background: transparent;")

        # Settings button
        self.settings_btn = QPushButton()
        settings_icon = load_svg_icon("settings", 18)
        if not settings_icon.isNull():
            self.settings_btn.setIcon(settings_icon)
        else:
            self.settings_btn.setText("\u2699")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self._style_control_button(self.settings_btn)

        # Window control buttons
        self.min_btn = QPushButton("\u2014")  # Em dash for minimize
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        self._style_control_button(self.min_btn)

        self.max_btn = QPushButton("\u25a1")  # Square for maximize
        self.max_btn.setFixedSize(32, 32)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.setToolTip("Maximize")
        self.max_btn.clicked.connect(self.maximize_clicked.emit)
        self._style_control_button(self.max_btn)

        self.close_btn = QPushButton("\u2715")  # X for close
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self._style_close_button(self.close_btn)

        # Layout
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addStretch()
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        # Title bar styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["bg_secondary"]};
                border-bottom: 1px solid {COLORS["border_default"]};
            }}
        """)

    def _style_control_button(self, btn: QPushButton):
        """Style a window control button."""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS["text_secondary"]};
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_hover"]};
                color: {COLORS["text_primary"]};
            }}
        """)

    def _style_close_button(self, btn: QPushButton):
        """Style the close button with red hover."""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS["text_secondary"]};
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_red"]};
                color: {COLORS["text_primary"]};
            }}
        """)

    def set_maximized_state(self, is_maximized: bool):
        """Update the maximize button icon based on window state."""
        self._is_maximized = is_maximized
        self.max_btn.setText("\u25a3" if is_maximized else "\u25a1")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging."""
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            # If maximized, restore first
            if self._is_maximized:
                self.maximize_clicked.emit()
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double-click to maximize/restore."""
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
