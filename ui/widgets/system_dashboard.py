"""
System monitoring dashboard with real-time charts using pyqtgraph.
"""

from collections import deque

import pyqtgraph as pg
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.styles.colors import COLORS
from ui.widgets.gradient_bar import GradientBar


def _section_header(text: str) -> QWidget:
    """Create a cyan-bar + uppercase label section header."""
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    bar = QFrame()
    bar.setFixedSize(2, 10)
    bar.setStyleSheet(f"background-color: {COLORS['accent_cyan']}; border-radius: 1px;")

    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 7, QFont.Bold))
    label.setStyleSheet(f"color: rgba(0, 212, 255, 0.7); letter-spacing: 2px; background: transparent;")

    layout.addWidget(bar)
    layout.addWidget(label)
    layout.addStretch()
    return container


class MetricPanel(QFrame):
    """Individual metric panel: label, value, gradient bar, and history chart."""

    _BAR_COLORS = {
        "CPU":  ("#00d4ff", "#0055aa"),
        "RAM":  ("#00cc66", "#005533"),
        "DISK": ("#ff8800", "#883300"),
    }

    def __init__(self, name: str, color: str, unit: str = "%", parent=None):
        super().__init__(parent)
        self._name = name
        self._color = color
        self._unit = unit
        self._history = deque([0] * 60, maxlen=60)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_secondary"]};
                border-radius: 6px;
                border: 1px solid {COLORS["border_default"]};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # Header: name (left) + value (right)
        header = QHBoxLayout()

        self.name_label = QLabel(self._name)
        self.name_label.setFont(QFont("Segoe UI", 7))
        self.name_label.setStyleSheet(
            f"color: rgba(255,255,255,0.4); letter-spacing: 1px; background: transparent;"
        )

        self.value_label = QLabel(f"0{self._unit}")
        self.value_label.setFont(QFont("Consolas", 9, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self._color}; background: transparent;")
        self.value_label.setAlignment(Qt.AlignRight)

        header.addWidget(self.name_label)
        header.addStretch()
        header.addWidget(self.value_label)

        # Gradient bar
        primary, dim = self._BAR_COLORS.get(self._name, (self._color, self._color))
        self.progress_bar = GradientBar(primary, dim)

        # Chart
        pg.setConfigOptions(antialias=True)
        self.chart = pg.PlotWidget()
        self.chart.setBackground(COLORS["bg_primary"])
        self.chart.setFixedHeight(44)
        self.chart.setMouseEnabled(x=False, y=False)
        self.chart.hideAxis("bottom")
        self.chart.hideAxis("left")
        self.chart.setYRange(0, 100)
        self.chart.setXRange(0, 60)

        pen = pg.mkPen(color=self._color, width=1.5)
        self.curve = self.chart.plot(pen=pen)
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotDataItem([0] * 60),
            brush=pg.mkBrush(self._color + "30"),
        )
        self.chart.addItem(self.fill)

        layout.addLayout(header)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.chart)

    def update_value(self, value: float, detail_text: str = None):
        value = min(max(value, 0), 100)
        self.value_label.setText(detail_text if detail_text else f"{value:.1f}{self._unit}")
        self.progress_bar.set_value(int(value))

        self._history.append(value)
        y_data = list(self._history)
        x_data = list(range(len(y_data)))
        self.curve.setData(x_data, y_data)

        self.chart.removeItem(self.fill)
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotDataItem(x_data, [0] * len(y_data)),
            brush=pg.mkBrush(self._color + "30"),
        )
        self.chart.addItem(self.fill)


class SystemDashboard(QWidget):
    """System monitoring dashboard with CPU, RAM, and Disk metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(_section_header("SYSTEM"))

        self.cpu_panel = MetricPanel("CPU", COLORS["chart_cpu"])
        self.ram_panel = MetricPanel("RAM", COLORS["chart_ram"])
        self.disk_panel = MetricPanel("DISK", COLORS["chart_disk"])

        self.info_frame = QFrame()
        self.info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_secondary"]};
                border-radius: 6px;
                border: 1px solid {COLORS["border_default"]};
            }}
        """)
        info_layout = QGridLayout(self.info_frame)
        info_layout.setContentsMargins(10, 6, 10, 6)
        info_layout.setSpacing(3)

        uptime_icon = QLabel("🕐")
        uptime_icon.setStyleSheet("background: transparent;")
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setFont(QFont("Segoe UI", 8))
        self.uptime_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        os_icon = QLabel("💻")
        os_icon.setStyleSheet("background: transparent;")
        self.os_label = QLabel("OS: --")
        self.os_label.setFont(QFont("Segoe UI", 8))
        self.os_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        info_layout.addWidget(uptime_icon, 0, 0)
        info_layout.addWidget(self.uptime_label, 0, 1)
        info_layout.addWidget(os_icon, 1, 0)
        info_layout.addWidget(self.os_label, 1, 1)
        info_layout.setColumnStretch(1, 1)

        layout.addWidget(self.cpu_panel)
        layout.addWidget(self.ram_panel)
        layout.addWidget(self.disk_panel)
        layout.addWidget(self.info_frame)
        layout.addStretch()

    @Slot(dict)
    def update_stats(self, stats: dict):
        self.cpu_panel.update_value(stats.get("cpu_percent", 0))

        ram_pct = stats.get("ram_percent", 0)
        ram_used = stats.get("ram_used_gb", 0)
        ram_total = stats.get("ram_total_gb", 0)
        self.ram_panel.update_value(ram_pct, f"{ram_used:.1f}/{ram_total:.1f}GB ({ram_pct:.0f}%)")

        disk_pct = stats.get("disk_percent", 0)
        disk_used = stats.get("disk_used_gb", 0)
        disk_total = stats.get("disk_total_gb", 0)
        self.disk_panel.update_value(disk_pct, f"{disk_used:.0f}/{disk_total:.0f}GB ({disk_pct:.0f}%)")

        self.uptime_label.setText(f"Uptime: {stats.get('uptime', '--')}")
        os_name = stats.get("os", "Unknown")
        os_ver = stats.get("os_version", "")
        self.os_label.setText(f"OS: {os_name} {os_ver}".strip())
