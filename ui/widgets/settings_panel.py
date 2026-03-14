"""
Settings panel dialog for ALFRED configuration.
"""

import json
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from ui.styles.colors import COLORS

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "settings.json")


def load_settings() -> dict:
    """Load settings from JSON file."""
    defaults = {
        "primary_model": "anthropic/claude-3.5-sonnet",
        "fallback_model": "openai/gpt-4o-mini",
        "voice_engine": "pyttsx3",
        "voice_rate": 100,
        "max_history": 10,
    }
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH) as f:
                saved = json.load(f)
                defaults.update(saved)
    except (json.JSONDecodeError, OSError):
        pass
    return defaults


def save_settings(settings: dict):
    """Save settings to JSON file."""
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


class SettingsPanel(QDialog):
    """Settings dialog for configuring ALFRED."""

    settings_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = load_settings()
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        """Set up the settings dialog."""
        self.setWindowTitle("A.L.F.R.E.D Settings")
        self.setFixedSize(450, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS["bg_primary"]};
                color: {COLORS["text_primary"]};
            }}
            QGroupBox {{
                background-color: {COLORS["bg_secondary"]};
                border: 1px solid {COLORS["border_default"]};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                font-weight: bold;
                color: {COLORS["accent_cyan"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }}
            QComboBox {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border_default"]};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 200px;
            }}
            QComboBox:hover {{
                border-color: {COLORS["accent_cyan"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border_default"]};
                selection-background-color: {COLORS["bg_hover"]};
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {COLORS["bg_tertiary"]};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background-color: {COLORS["accent_cyan"]};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {COLORS["accent_cyan_dim"]};
                border-radius: 3px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        layout.addWidget(title)

        # LLM Section
        llm_group = QGroupBox("Language Model")
        llm_layout = QVBoxLayout(llm_group)

        llm_layout.addWidget(QLabel("Primary Model:"))
        self.primary_model = QComboBox()
        self.primary_model.addItems(
            [
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "google/gemini-pro",
            ]
        )
        llm_layout.addWidget(self.primary_model)

        llm_layout.addWidget(QLabel("Fallback Model:"))
        self.fallback_model = QComboBox()
        self.fallback_model.addItems(
            [
                "openai/gpt-4o-mini",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o",
                "anthropic/claude-3.5-sonnet",
            ]
        )
        llm_layout.addWidget(self.fallback_model)

        # Max history
        history_row = QHBoxLayout()
        history_row.addWidget(QLabel("Conversation History:"))
        self.history_value_label = QLabel("10")
        self.history_value_label.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        history_row.addWidget(self.history_value_label)
        llm_layout.addLayout(history_row)

        self.max_history = QSlider(Qt.Horizontal)
        self.max_history.setRange(5, 50)
        self.max_history.setValue(10)
        self.max_history.valueChanged.connect(lambda v: self.history_value_label.setText(str(v)))
        llm_layout.addWidget(self.max_history)

        layout.addWidget(llm_group)

        # Voice Section
        voice_group = QGroupBox("Voice")
        voice_layout = QVBoxLayout(voice_group)

        voice_layout.addWidget(QLabel("Voice Engine:"))
        self.voice_engine = QComboBox()
        self.voice_engine.addItems(["pyttsx3", "ElevenLabs"])
        voice_layout.addWidget(self.voice_engine)

        # Voice rate
        rate_row = QHBoxLayout()
        rate_row.addWidget(QLabel("Voice Rate:"))
        self.rate_value_label = QLabel("100")
        self.rate_value_label.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        rate_row.addWidget(self.rate_value_label)
        voice_layout.addLayout(rate_row)

        self.voice_rate = QSlider(Qt.Horizontal)
        self.voice_rate.setRange(50, 200)
        self.voice_rate.setValue(100)
        self.voice_rate.valueChanged.connect(lambda v: self.rate_value_label.setText(str(v)))
        voice_layout.addWidget(self.voice_rate)

        layout.addWidget(voice_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border_default"]};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedSize(100, 36)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent_cyan"]};
                color: {COLORS["bg_primary"]};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_cyan_dim"]};
            }}
        """)
        apply_btn.clicked.connect(self._apply_settings)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        layout.addLayout(button_layout)

    def _load_values(self):
        """Load current settings into the UI."""
        idx = self.primary_model.findText(self._settings.get("primary_model", ""))
        if idx >= 0:
            self.primary_model.setCurrentIndex(idx)

        idx = self.fallback_model.findText(self._settings.get("fallback_model", ""))
        if idx >= 0:
            self.fallback_model.setCurrentIndex(idx)

        self.voice_engine.setCurrentText(self._settings.get("voice_engine", "pyttsx3"))
        self.voice_rate.setValue(self._settings.get("voice_rate", 100))
        self.max_history.setValue(self._settings.get("max_history", 10))

    def _apply_settings(self):
        """Apply and save the settings."""
        self._settings = {
            "primary_model": self.primary_model.currentText(),
            "fallback_model": self.fallback_model.currentText(),
            "voice_engine": self.voice_engine.currentText(),
            "voice_rate": self.voice_rate.value(),
            "max_history": self.max_history.value(),
        }
        save_settings(self._settings)
        self.settings_changed.emit(self._settings)
        self.accept()
