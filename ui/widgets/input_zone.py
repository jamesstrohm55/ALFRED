"""
Unified input zone: text input, voice button, and inline waveform in one adaptive widget.

Three states:
  IDLE     — input field + mic + send button; no waveform
  LISTENING — zone expands to show cyan input waveform inline
  SPEAKING  — zone expands to show green output waveform inline
"""

import contextlib
import random

import numpy as np
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.signals import signals
from ui.styles.colors import COLORS

# ---------------------------------------------------------------------------
# HistoryLineEdit
# ---------------------------------------------------------------------------


class HistoryLineEdit(QLineEdit):
    """QLineEdit with up/down arrow key command history navigation."""

    history_up = Signal()
    history_down = Signal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.history_up.emit()
        elif event.key() == Qt.Key_Down:
            self.history_down.emit()
        else:
            super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# WaveformCanvas
# ---------------------------------------------------------------------------


class WaveformCanvas(QWidget):
    """Draws amplitude bars via QPainter. Updated by InputZone."""

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self._color = color
        self._num_bars = 20
        self._amplitudes = [0.0] * self._num_bars
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_amplitudes(self, amplitudes: list[float]) -> None:
        self._amplitudes = amplitudes
        self.update()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center_y = h // 2

        painter.fillRect(self.rect(), Qt.transparent)

        if w == 0:
            return

        bar_w = 3
        spacing = max(bar_w + 1, w // self._num_bars)
        max_h = max(1, center_y - 4)

        for i, amp in enumerate(self._amplitudes):
            x = i * spacing
            bar_h = max(2, int(amp * max_h))
            bar_color = QColor(self._color)
            bar_color.setAlpha(int(100 + amp * 155))
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, center_y - bar_h, bar_w, bar_h * 2, 1, 1)


# ---------------------------------------------------------------------------
# InputZone
# ---------------------------------------------------------------------------


class InputZone(QWidget):
    """
    Adaptive input zone with three visual states.

    Public API (matches former InputBar):
      text_submitted      Signal(str)
      voice_button_clicked Signal()
      set_enabled(bool)
      focus_input()

    New API:
      set_state(str)                  — IDLE / LISTENING / SPEAKING
      on_listening_state_changed(bool)
      update_input_waveform(ndarray)
      update_output_waveform(ndarray)
      state -> str                    (property)
    """

    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"

    text_submitted = Signal(str)
    voice_button_clicked = Signal()

    MAX_HISTORY = 50
    _NUM_BARS = 20
    _WAVEFORM_HEIGHT = 44

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = self.IDLE
        self._history: list[str] = []
        self._history_index = -1
        self._current_text = ""

        # Waveform amplitude state
        self._amplitudes = [0.0] * self._NUM_BARS
        self._target_amplitudes = [0.0] * self._NUM_BARS
        self._simulating = False
        self._attack = 0.3
        self._decay = 0.15

        self._setup_ui()
        self._setup_animation()
        self._setup_waveform_timer()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 4, 10, 8)
        outer.setSpacing(0)

        self._container = QFrame()
        self._container.setObjectName("inputZoneContainer")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # — Waveform row (hidden by default via maximumHeight=0) —
        self._waveform_row = QWidget()
        self._waveform_row.setMaximumHeight(0)
        self._waveform_row.setStyleSheet("background: transparent;")
        wf_layout = QHBoxLayout(self._waveform_row)
        wf_layout.setContentsMargins(14, 6, 14, 4)
        wf_layout.setSpacing(10)

        self._state_label = QLabel("LISTENING")
        self._state_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self._state_label.setStyleSheet("color: rgba(0, 212, 255, 0.6); letter-spacing: 2px; background: transparent;")
        self._state_label.setFixedWidth(110)

        self._waveform_canvas = WaveformCanvas(QColor(COLORS["accent_cyan"]))
        self._waveform_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        wf_layout.addWidget(self._state_label)
        wf_layout.addWidget(self._waveform_canvas, stretch=1)

        # — Input row —
        input_row = QWidget()
        input_row.setStyleSheet("background: transparent;")
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(8, 6, 8, 6)
        input_layout.setSpacing(8)

        self._mic_button = QPushButton("🎤")
        self._mic_button.setFixedSize(36, 36)
        self._mic_button.setCursor(Qt.PointingHandCursor)
        self._mic_button.setToolTip("Click to speak")
        self._mic_button.clicked.connect(self._on_mic_clicked)

        self._text_input = HistoryLineEdit()
        self._text_input.setPlaceholderText("Ask ALFRED anything...")
        self._text_input.setFont(QFont("Segoe UI", 10))
        self._text_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._text_input.setMinimumHeight(36)
        self._text_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {COLORS["text_primary"]};
                border: none;
                padding: 0 8px;
                selection-background-color: {COLORS["accent_cyan"]};
            }}
        """)
        self._text_input.returnPressed.connect(self._on_send_clicked)
        self._text_input.history_up.connect(self._on_history_up)
        self._text_input.history_down.connect(self._on_history_down)

        self._send_button = QPushButton("↑")
        self._send_button.setFixedSize(36, 36)
        self._send_button.setCursor(Qt.PointingHandCursor)
        self._send_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._send_button.setToolTip("Send message")
        self._send_button.clicked.connect(self._on_send_clicked)
        # Apply initial styles after both buttons exist (_apply_mic_idle_style also touches _send_button)
        self._apply_mic_idle_style()
        self._apply_send_style()

        input_layout.addWidget(self._mic_button)
        input_layout.addWidget(self._text_input, stretch=1)
        input_layout.addWidget(self._send_button)

        container_layout.addWidget(self._waveform_row)
        container_layout.addWidget(input_row)

        self._apply_container_idle_style()
        outer.addWidget(self._container)

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self._waveform_row, b"maximumHeight")
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def _expand_waveform(self):
        self._anim.stop()
        self._anim.setDuration(200)
        self._anim.setStartValue(self._waveform_row.maximumHeight())
        self._anim.setEndValue(self._WAVEFORM_HEIGHT)
        self._anim.start()

    def _collapse_waveform(self):
        self._anim.stop()
        self._anim.setDuration(150)
        self._anim.setStartValue(self._waveform_row.maximumHeight())
        self._anim.setEndValue(0)
        self._anim.start()

    # ------------------------------------------------------------------
    # Waveform timer
    # ------------------------------------------------------------------

    def _setup_waveform_timer(self):
        self._wf_timer = QTimer()
        self._wf_timer.timeout.connect(self._tick_waveform)
        self._wf_timer.start(33)  # ~30 fps

    def _tick_waveform(self):
        if self._simulating:
            for i in range(self._NUM_BARS):
                base = 0.25 + random.random() * 0.55
                pos_factor = 1.0 - abs(i - self._NUM_BARS / 2) / (self._NUM_BARS / 2) * 0.3
                self._target_amplitudes[i] = base * pos_factor

        changed = False
        for i in range(self._NUM_BARS):
            cur = self._amplitudes[i]
            tgt = self._target_amplitudes[i]
            if cur < tgt:
                self._amplitudes[i] = min(cur + self._attack, tgt)
                changed = True
            elif cur > tgt:
                self._amplitudes[i] = max(cur - self._decay, tgt)
                changed = True
            if self._state == self.IDLE and not self._simulating:
                self._target_amplitudes[i] = 0.0

        if changed or self._state != self.IDLE:
            self._waveform_canvas.set_amplitudes(list(self._amplitudes))

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str) -> None:
        if state == self._state:
            return
        self._state = state

        if state == self.IDLE:
            self._simulating = False
            self._collapse_waveform()
            self._apply_container_idle_style()
            self._apply_mic_idle_style()
            self._apply_send_style()
            self._text_input.setEnabled(True)

        elif state == self.LISTENING:
            self._simulating = False
            self._state_label.setText("LISTENING")
            self._state_label.setStyleSheet(
                "color: rgba(0, 212, 255, 0.6); letter-spacing: 2px; background: transparent;"
            )
            self._waveform_canvas._color = QColor(COLORS["waveform_input"])
            self._expand_waveform()
            self._apply_container_listening_style()
            self._apply_mic_listening_style()

        elif state == self.SPEAKING:
            self._simulating = True
            self._state_label.setText("ALFRED SPEAKING")
            self._state_label.setStyleSheet(
                "color: rgba(0, 204, 102, 0.7); letter-spacing: 2px; background: transparent;"
            )
            self._waveform_canvas._color = QColor(COLORS["waveform_output"])
            self._expand_waveform()
            self._apply_container_speaking_style()
            self._apply_stop_style()
            self._text_input.setEnabled(False)

    @Slot(bool)
    def on_listening_state_changed(self, is_listening: bool) -> None:
        self.set_state(self.LISTENING if is_listening else self.IDLE)

    # ------------------------------------------------------------------
    # Waveform data slots
    # ------------------------------------------------------------------

    @Slot(object)
    def update_input_waveform(self, audio_chunk) -> None:
        if audio_chunk is None or len(audio_chunk) == 0:
            return
        chunk = np.array(audio_chunk) if not isinstance(audio_chunk, np.ndarray) else audio_chunk
        normalized = np.clip(np.abs(chunk) / 32768.0, 0, 1)
        spb = max(1, len(normalized) // self._NUM_BARS)
        for i in range(self._NUM_BARS):
            band = normalized[i * spb : min((i + 1) * spb, len(normalized))]
            if len(band):
                self._target_amplitudes[i] = min(1.0, float(np.sqrt(np.mean(band**2))) * 8.0)

    @Slot(object)
    def update_output_waveform(self, audio_chunk) -> None:
        self.update_input_waveform(audio_chunk)

    # ------------------------------------------------------------------
    # Styling helpers
    # ------------------------------------------------------------------

    def _apply_container_idle_style(self):
        self._container.setStyleSheet("""
            QFrame#inputZoneContainer {
                background-color: #080812;
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 12px;
            }
        """)

    def _apply_container_listening_style(self):
        self._container.setStyleSheet("""
            QFrame#inputZoneContainer {
                background-color: #080812;
                border: 1px solid rgba(0, 212, 255, 0.40);
                border-radius: 12px;
            }
        """)

    def _apply_container_speaking_style(self):
        self._container.setStyleSheet("""
            QFrame#inputZoneContainer {
                background-color: #080812;
                border: 1px solid rgba(0, 204, 102, 0.30);
                border-radius: 12px;
            }
        """)

    def _apply_mic_idle_style(self):
        self._send_button.setText("↑")
        self._send_button.setToolTip("Send message")
        with contextlib.suppress(RuntimeError):
            self._send_button.clicked.disconnect()
        self._send_button.clicked.connect(self._on_send_clicked)
        self._mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1.5px solid rgba(0, 212, 255, 0.3);
                border-radius: 18px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                border-color: {COLORS["accent_cyan"]};
                background-color: rgba(0, 212, 255, 0.06);
            }}
        """)

    def _apply_mic_listening_style(self):
        self._mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 212, 255, 0.12);
                border: 2px solid {COLORS["accent_cyan"]};
                border-radius: 18px;
                font-size: 16px;
            }}
        """)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(12)
        glow.setColor(Qt.cyan)
        glow.setOffset(0, 0)
        self._mic_button.setGraphicsEffect(glow)

    def _apply_send_style(self):
        self._mic_button.setGraphicsEffect(None)
        self._send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 212, 255, 0.15);
                color: {COLORS["accent_cyan"]};
                border: 1px solid rgba(0, 212, 255, 0.30);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 212, 255, 0.25);
            }}
            QPushButton:disabled {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_disabled"]};
                border-color: {COLORS["border_default"]};
            }}
        """)

    def _apply_stop_style(self):
        self._send_button.setText("■")
        self._send_button.setToolTip("Stop speaking")
        with contextlib.suppress(RuntimeError):
            self._send_button.clicked.disconnect()
        self._send_button.clicked.connect(self._on_stop_clicked)
        self._send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 204, 102, 0.15);
                color: {COLORS["accent_green"]};
                border: 1.5px solid rgba(0, 204, 102, 0.40);
                border-radius: 18px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 204, 102, 0.25);
            }}
        """)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_send_clicked(self):
        text = self._text_input.text().strip()
        if not text:
            return
        if not self._history or self._history[-1] != text:
            self._history.append(text)
            if len(self._history) > self.MAX_HISTORY:
                self._history.pop(0)
        self._history_index = -1
        self._current_text = ""
        self._text_input.clear()
        self.text_submitted.emit(text)

    def _on_mic_clicked(self):
        if self._state != self.LISTENING:
            self.voice_button_clicked.emit()

    def _on_stop_clicked(self):
        signals.speaking_finished.emit()

    def _on_history_up(self):
        if not self._history:
            return
        if self._history_index == -1:
            self._current_text = self._text_input.text()
            self._history_index = len(self._history) - 1
        elif self._history_index > 0:
            self._history_index -= 1
        self._text_input.setText(self._history[self._history_index])

    def _on_history_down(self):
        if self._history_index == -1:
            return
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._text_input.setText(self._history[self._history_index])
        else:
            self._history_index = -1
            self._text_input.setText(self._current_text)

    # ------------------------------------------------------------------
    # Public API (matches former InputBar)
    # ------------------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        if self._state != self.SPEAKING:
            self._text_input.setEnabled(enabled)
        self._send_button.setEnabled(enabled)
        self._mic_button.setEnabled(enabled)

    def focus_input(self) -> None:
        self._text_input.setFocus()

    def set_listening_state(self, is_listening: bool) -> None:
        """Compatibility alias — prefer on_listening_state_changed."""
        self.on_listening_state_changed(is_listening)
