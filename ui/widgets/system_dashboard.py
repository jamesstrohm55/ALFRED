"""
System monitoring dashboard with real-time charts using pyqtgraph.
"""
from collections import deque
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QGridLayout
)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont

import pyqtgraph as pg
import numpy as np

from ui.styles.colors import COLORS


class MetricPanel(QFrame):
    """Individual metric panel with label, value, progress bar, and chart."""

    def __init__(self, name: str, color: str, unit: str = "%", parent=None):
        super().__init__(parent)
        self._name = name
        self._color = color
        self._unit = unit
        self._history = deque([0] * 60, maxlen=60)  # 60 seconds of history

        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border_default']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header row with name and value
        header_layout = QHBoxLayout()

        # Metric name
        self.name_label = QLabel(self._name)
        self.name_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.name_label.setStyleSheet(f"color: {self._color}; background: transparent;")

        # Current value
        self.value_label = QLabel(f"0{self._unit}")
        self.value_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        self.value_label.setAlignment(Qt.AlignRight)

        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.value_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_primary']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {self._color};
                border-radius: 3px;
            }}
        """)

        # Chart using pyqtgraph
        pg.setConfigOptions(antialias=True)
        self.chart = pg.PlotWidget()
        self.chart.setBackground(COLORS['bg_primary'])
        self.chart.setFixedHeight(50)
        self.chart.setMouseEnabled(x=False, y=False)
        self.chart.hideAxis('bottom')
        self.chart.hideAxis('left')
        self.chart.setYRange(0, 100)
        self.chart.setXRange(0, 60)

        # Create the plot curve
        pen = pg.mkPen(color=self._color, width=2)
        self.curve = self.chart.plot(pen=pen)

        # Fill under curve
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotDataItem([0] * 60),
            brush=pg.mkBrush(self._color + '40')  # 25% opacity
        )
        self.chart.addItem(self.fill)

        layout.addLayout(header_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.chart)

    def update_value(self, value: float, detail_text: str = None):
        """Update the metric value."""
        value = min(max(value, 0), 100)  # Clamp to 0-100

        # Update labels
        if detail_text:
            self.value_label.setText(detail_text)
        else:
            self.value_label.setText(f"{value:.1f}{self._unit}")

        # Update progress bar
        self.progress_bar.setValue(int(value))

        # Update history
        self._history.append(value)

        # Update chart
        y_data = list(self._history)
        x_data = list(range(len(y_data)))
        self.curve.setData(x_data, y_data)

        # Update fill
        self.chart.removeItem(self.fill)
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotDataItem(x_data, [0] * len(y_data)),
            brush=pg.mkBrush(self._color + '40')
        )
        self.chart.addItem(self.fill)


class SystemDashboard(QWidget):
    """System monitoring dashboard with CPU, RAM, and Disk metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Title
        title = QLabel("SYSTEM MONITOR")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            padding: 8px;
            background-color: {COLORS['bg_secondary']};
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Metric panels
        self.cpu_panel = MetricPanel("CPU", COLORS['chart_cpu'])
        self.ram_panel = MetricPanel("RAM", COLORS['chart_ram'])
        self.disk_panel = MetricPanel("DISK", COLORS['chart_disk'])

        # Info panel for uptime and OS
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border_default']};
            }}
        """)
        info_layout = QGridLayout(self.info_frame)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.setSpacing(4)

        # Uptime
        uptime_icon = QLabel("\U0001F551")  # Clock emoji
        uptime_icon.setStyleSheet("background: transparent;")
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setFont(QFont("Segoe UI", 9))
        self.uptime_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        # OS Info
        os_icon = QLabel("\U0001F4BB")  # Computer emoji
        os_icon.setStyleSheet("background: transparent;")
        self.os_label = QLabel("OS: --")
        self.os_label.setFont(QFont("Segoe UI", 9))
        self.os_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        info_layout.addWidget(uptime_icon, 0, 0)
        info_layout.addWidget(self.uptime_label, 0, 1)
        info_layout.addWidget(os_icon, 1, 0)
        info_layout.addWidget(self.os_label, 1, 1)
        info_layout.setColumnStretch(1, 1)

        # Add all to layout
        layout.addWidget(title)
        layout.addWidget(self.cpu_panel)
        layout.addWidget(self.ram_panel)
        layout.addWidget(self.disk_panel)
        layout.addWidget(self.info_frame)
        layout.addStretch()

    @Slot(dict)
    def update_stats(self, stats: dict):
        """Update the dashboard with new system statistics."""
        # Update CPU
        cpu_percent = stats.get('cpu_percent', 0)
        self.cpu_panel.update_value(cpu_percent)

        # Update RAM
        ram_percent = stats.get('ram_percent', 0)
        ram_used = stats.get('ram_used_gb', 0)
        ram_total = stats.get('ram_total_gb', 0)
        ram_detail = f"{ram_used:.1f} / {ram_total:.1f} GB ({ram_percent:.0f}%)"
        self.ram_panel.update_value(ram_percent, ram_detail)

        # Update Disk
        disk_percent = stats.get('disk_percent', 0)
        disk_used = stats.get('disk_used_gb', 0)
        disk_total = stats.get('disk_total_gb', 0)
        disk_detail = f"{disk_used:.0f} / {disk_total:.0f} GB ({disk_percent:.0f}%)"
        self.disk_panel.update_value(disk_percent, disk_detail)

        # Update info
        uptime = stats.get('uptime', '--')
        self.uptime_label.setText(f"Uptime: {uptime}")

        os_name = stats.get('os', 'Unknown')
        os_version = stats.get('os_version', '')
        if os_version:
            self.os_label.setText(f"OS: {os_name} {os_version}")
        else:
            self.os_label.setText(f"OS: {os_name}")
