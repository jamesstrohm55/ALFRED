"""
Custom frameless title bar for ALFRED main window.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.styles.colors import COLORS
from ui.utils import load_svg_icon


class CustomTitleBar(QWidget):
    """Custom draggable title bar with minimize, maximize, close, and settings buttons."""

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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(8)

        # Circle logo with cyan glow
        logo = QLabel("A")
        logo.setFixedSize(22, 22)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 9, QFont.Bold))
        logo.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["accent_cyan"]};
                background-color: {COLORS["bg_primary"]};
                border: 1.5px solid {COLORS["accent_cyan"]};
                border-radius: 11px;
            }}
        """)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(10)
        glow.setColor(Qt.cyan)
        glow.setOffset(0, 0)
        logo.setGraphicsEffect(glow)

        # App name (white, wide letter-spacing via spaces)
        title = QLabel("A . L . F . R . E . D")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")

        # Status dot
        status = QLabel("● ONLINE")
        status.setFont(QFont("Segoe UI", 7))
        status.setStyleSheet(f"color: rgba(0, 212, 255, 0.45); background: transparent;")

        # Settings button
        self.settings_btn = QPushButton()
        settings_icon = load_svg_icon("settings", 16)
        if not settings_icon.isNull():
            self.settings_btn.setIcon(settings_icon)
        else:
            self.settings_btn.setText("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self._style_control_btn(self.settings_btn, hover_red=False)

        # Window controls
        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        self._style_control_btn(self.min_btn, hover_red=False)

        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(30, 30)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.setToolTip("Maximize")
        self.max_btn.clicked.connect(self.maximize_clicked.emit)
        self._style_control_btn(self.max_btn, hover_red=False)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self._style_control_btn(self.close_btn, hover_red=True)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141428, stop:1 #0f0f20
                );
                border-bottom: 1px solid rgba(0, 212, 255, 0.15);
            }}
        """)

    def _style_control_btn(self, btn: QPushButton, hover_red: bool):
        if hover_red:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.45);
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 60, 60, 0.2);
                    color: #ff6060;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.45);
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.07);
                    color: rgba(255, 255, 255, 0.9);
                }
            """)

    def set_maximized_state(self, is_maximized: bool):
        self._is_maximized = is_maximized
        self.max_btn.setText("❐" if is_maximized else "□")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            if self._is_maximized:
                self.maximize_clicked.emit()
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
