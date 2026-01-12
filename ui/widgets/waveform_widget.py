"""
Real-time audio waveform visualizer widget using QPainter.
"""
import numpy as np
from collections import deque
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Slot, Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QFont, QLinearGradient, QBrush

from ui.styles.colors import COLORS


class WaveformWidget(QWidget):
    """Real-time audio waveform visualizer using amplitude bars."""

    def __init__(self, mode: str = 'input', parent=None):
        """
        Initialize the waveform widget.

        Args:
            mode: 'input' for microphone visualization, 'output' for TTS visualization
            parent: Parent widget
        """
        super().__init__(parent)
        self._mode = mode
        self._num_bars = 32  # Number of amplitude bars
        self._amplitudes = [0.0] * self._num_bars
        self._target_amplitudes = [0.0] * self._num_bars
        self._is_active = False
        self._simulating = False

        # Colors based on mode
        if mode == 'input':
            self._color = QColor(COLORS['waveform_input'])
            self._label_text = "INPUT"
        else:
            self._color = QColor(COLORS['waveform_output'])
            self._label_text = "OUTPUT"

        self._setup_ui()

        # Animation timer for smooth updates
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(33)  # ~30 FPS

        # Smoothing factors
        self._attack = 0.3   # How fast bars rise
        self._decay = 0.15   # How fast bars fall

    def _setup_ui(self):
        """Set up the widget UI."""
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

        # Main styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['waveform_bg']};
                border-radius: 8px;
            }}
        """)

    def paintEvent(self, event):
        """Custom paint event for waveform rendering."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get dimensions
        width = self.width()
        height = self.height()
        center_y = height // 2

        # Draw background
        painter.fillRect(self.rect(), QColor(COLORS['waveform_bg']))

        # Draw center line
        painter.setPen(QPen(QColor(COLORS['border_default']), 1))
        painter.drawLine(0, center_y, width, center_y)

        # Draw mode label
        painter.setPen(QPen(QColor(COLORS['text_disabled']), 1))
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.drawText(8, 14, self._label_text)

        # Draw amplitude bars
        self._draw_bars(painter, width, height, center_y)

        # Draw border
        painter.setPen(QPen(QColor(COLORS['border_default']), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 8, 8)

    def _draw_bars(self, painter: QPainter, width: int, height: int, center_y: int):
        """Draw amplitude bars visualization."""
        padding = 40  # Left padding for label
        bar_area_width = width - padding - 10
        bar_width = max(2, (bar_area_width / self._num_bars) - 2)
        spacing = bar_area_width / self._num_bars
        max_bar_height = (height // 2) - 8

        # Create gradient brush
        gradient = QLinearGradient(0, center_y - max_bar_height, 0, center_y + max_bar_height)
        color_bright = QColor(self._color)
        color_dim = QColor(self._color)
        color_dim.setAlpha(100)
        gradient.setColorAt(0, color_bright)
        gradient.setColorAt(0.5, color_dim)
        gradient.setColorAt(1, color_bright)

        painter.setPen(Qt.NoPen)

        for i, amp in enumerate(self._amplitudes):
            x = padding + (i * spacing)
            bar_height = max(2, amp * max_bar_height)

            # Draw bar extending both up and down from center
            rect_top = center_y - bar_height
            rect_height = bar_height * 2

            # Use solid color with varying alpha based on amplitude
            bar_color = QColor(self._color)
            bar_color.setAlpha(int(150 + (amp * 105)))  # 150-255 alpha range
            painter.setBrush(QBrush(bar_color))

            # Draw rounded rectangle bar
            painter.drawRoundedRect(
                int(x), int(rect_top),
                int(bar_width), int(rect_height),
                2, 2
            )

    def _on_timer(self):
        """Timer callback for smooth animation."""
        # Generate simulated data if in simulation mode
        if self._simulating:
            self._generate_simulated_data()

        needs_update = False

        for i in range(self._num_bars):
            current = self._amplitudes[i]
            target = self._target_amplitudes[i]

            if current < target:
                # Rising - use attack speed
                self._amplitudes[i] = min(current + self._attack, target)
                needs_update = True
            elif current > target:
                # Falling - use decay speed
                self._amplitudes[i] = max(current - self._decay, target)
                needs_update = True

            # Clear targets when not active (natural decay to zero)
            if not self._is_active and not self._simulating:
                self._target_amplitudes[i] = 0.0

        if needs_update or self._is_active or self._simulating:
            self.update()

    @Slot(object)
    def update_data(self, audio_chunk):
        """
        Update the waveform with new audio data.

        Args:
            audio_chunk: numpy array of audio samples (int16 or float32)
        """
        if audio_chunk is None or len(audio_chunk) == 0:
            return

        self._is_active = True

        # Convert to numpy if needed
        if not isinstance(audio_chunk, np.ndarray):
            audio_chunk = np.array(audio_chunk)

        # Normalize to 0-1 range based on int16 max value
        # This gives consistent scaling regardless of actual volume
        normalized = np.abs(audio_chunk) / 32768.0
        normalized = np.clip(normalized, 0, 1)

        # Split into bands for each bar
        samples_per_bar = len(normalized) // self._num_bars
        if samples_per_bar < 1:
            samples_per_bar = 1

        for i in range(self._num_bars):
            start_idx = i * samples_per_bar
            end_idx = min(start_idx + samples_per_bar, len(normalized))

            if start_idx < len(normalized):
                # Use RMS (root mean square) for smoother amplitude
                band = normalized[start_idx:end_idx]
                rms = np.sqrt(np.mean(band ** 2))
                # Apply strong boost for visibility and clamp
                amplitude = min(1.0, rms * 8.0)
                self._target_amplitudes[i] = amplitude

    def set_active(self, active: bool):
        """Set whether the waveform is actively receiving data."""
        self._is_active = active

    def start_simulation(self):
        """Start simulated waveform animation (for TTS output)."""
        self._is_active = True
        self._simulating = True

    def stop_simulation(self):
        """Stop simulated waveform animation."""
        self._simulating = False
        # Let decay handle the fade out

    def _generate_simulated_data(self):
        """Generate random waveform-like data for simulation."""
        import random
        for i in range(self._num_bars):
            # Generate smooth random amplitudes
            base = 0.3 + random.random() * 0.5
            # Add some variation based on position (higher in middle)
            position_factor = 1.0 - abs(i - self._num_bars / 2) / (self._num_bars / 2) * 0.3
            self._target_amplitudes[i] = base * position_factor

    def clear(self):
        """Clear the waveform."""
        self._amplitudes = [0.0] * self._num_bars
        self._target_amplitudes = [0.0] * self._num_bars
        self._is_active = False
        self._simulating = False
        self.update()


class DualWaveformWidget(QWidget):
    """Widget containing both input and output waveforms."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the dual waveform layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Input waveform (microphone)
        self.input_waveform = WaveformWidget(mode='input')

        # Output waveform (TTS)
        self.output_waveform = WaveformWidget(mode='output')

        layout.addWidget(self.input_waveform)
        layout.addWidget(self.output_waveform)

    @Slot(object)
    def update_input(self, audio_data):
        """Update the input waveform."""
        self.input_waveform.update_data(audio_data)

    @Slot(object)
    def update_output(self, audio_data):
        """Update the output waveform."""
        self.output_waveform.update_data(audio_data)

    def start_output_simulation(self):
        """Start simulated animation on output waveform (when ALFRED speaks)."""
        self.output_waveform.start_simulation()

    def stop_output_simulation(self):
        """Stop simulated animation on output waveform."""
        self.output_waveform.stop_simulation()
