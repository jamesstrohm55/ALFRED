"""
Main window for the ALFRED GUI application.
Frameless window with custom title bar, collapsible sidebar, and status bar.
"""

from PySide6.QtCore import Qt, QThreadPool, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSizeGrip, QVBoxLayout, QWidget

from ui.signals import signals
from ui.styles.colors import COLORS
from ui.styles.dark_theme import DARK_THEME_QSS
from ui.threads.audio_thread import AudioCaptureThread
from ui.threads.command_worker import CommandWorker, QuickActionWorker
from ui.threads.system_monitor_thread import SystemMonitorThread
from ui.widgets.chat_widget import ChatWidget
from ui.widgets.input_zone import InputZone
from ui.widgets.quick_actions import QuickActionsWidget
from ui.widgets.settings_panel import SettingsPanel
from ui.widgets.sidebar import CollapsibleSidebar
from ui.widgets.status_bar import StatusBar
from ui.widgets.system_dashboard import SystemDashboard
from ui.widgets.title_bar import CustomTitleBar


class MainWindow(QMainWindow):
    """Main application window for ALFRED."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._setup_threads()
        self._connect_signals()
        self._setup_shortcuts()

        self.chat_widget.add_message(
            "A.L.F.R.E.D",
            "Hello! I'm **A.L.F.R.E.D**, your personal assistant. How can I help you today?",
        )
        self.status_bar.set_llm_status("Claude 3.5 Sonnet", True)

    def _setup_window(self):
        self.setWindowTitle("A.L.F.R.E.D")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(DARK_THEME_QSS)

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralFrame")
        central_widget.setStyleSheet(f"""
            #centralFrame {{
                background-color: {COLORS["bg_primary"]};
                border: 1px solid {COLORS["border_default"]};
                border-radius: 10px;
            }}
        """)
        self.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(1, 1, 1, 1)
        main_v_layout.setSpacing(0)

        self.title_bar = CustomTitleBar()
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.settings_clicked.connect(self._open_settings)
        main_v_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 8, 10, 0)
        content_layout.setSpacing(10)

        self.sidebar = CollapsibleSidebar()
        self._setup_sidebar()
        right_panel = self._create_right_panel()

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(right_panel, stretch=1)
        main_v_layout.addWidget(content_widget, stretch=1)

        self.status_bar = StatusBar()
        main_v_layout.addWidget(self.status_bar)

        self._size_grip = QSizeGrip(central_widget)
        self._size_grip.setFixedSize(16, 16)
        self._size_grip.setStyleSheet("background: transparent;")

    def _setup_sidebar(self):
        self.system_dashboard = SystemDashboard()
        self.quick_actions = QuickActionsWidget()
        self.sidebar.add_widget(self.system_dashboard)
        self.sidebar.add_widget(self.quick_actions)
        self.sidebar.add_stretch()

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.chat_widget = ChatWidget()
        self.input_zone = InputZone()

        layout.addWidget(self.chat_widget, stretch=1)
        layout.addWidget(self.input_zone)
        return panel

    def _setup_threads(self):
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)

        self.system_monitor_thread = SystemMonitorThread(interval_ms=1000)
        self.system_monitor_thread.stats_updated.connect(self.system_dashboard.update_stats)
        self.system_monitor_thread.start()

        self.audio_thread = AudioCaptureThread()
        self.audio_thread.audio_chunk.connect(self.input_zone.update_input_waveform)
        self.audio_thread.speech_recognized.connect(self._on_speech_recognized)
        self.audio_thread.listening_state_changed.connect(self._on_listening_state_changed)
        self.audio_thread.error_occurred.connect(self._on_audio_error)
        self.audio_thread.start()

    def _connect_signals(self):
        self.input_zone.text_submitted.connect(self._on_text_submitted)
        self.input_zone.voice_button_clicked.connect(self._on_voice_button_clicked)
        self.quick_actions.action_triggered.connect(self._on_quick_action)

        signals.response_ready.connect(self._on_response_ready)
        signals.output_audio_data.connect(self.input_zone.update_output_waveform)

        signals.speaking_started.connect(lambda: self.input_zone.set_state(InputZone.SPEAKING))
        signals.speaking_started.connect(lambda: self.status_bar.set_speaking(True))
        signals.speaking_finished.connect(lambda: self.input_zone.set_state(InputZone.IDLE))
        signals.speaking_finished.connect(lambda: self.status_bar.set_speaking(False))

        signals.llm_status_changed.connect(self.status_bar.set_llm_status)

    def _setup_shortcuts(self):
        toggle_sidebar = QShortcut(QKeySequence("Ctrl+B"), self)
        toggle_sidebar.activated.connect(self.sidebar.toggle)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.title_bar.set_maximized_state(False)
        else:
            self.showMaximized()
            self.title_bar.set_maximized_state(True)

    def _open_settings(self):
        dialog = SettingsPanel(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    @Slot(dict)
    def _on_settings_changed(self, settings: dict):
        signals.settings_changed.emit(settings)

    @Slot(str)
    def _on_text_submitted(self, text: str):
        if not text.strip():
            return
        self.chat_widget.add_message("You", text)
        self.chat_widget.show_typing()
        self.input_zone.set_enabled(False)

        worker = CommandWorker(text)
        worker.signals.finished.connect(self._on_command_finished)
        worker.signals.error.connect(self._on_command_error)
        worker.signals.speaking_started.connect(lambda: signals.speaking_started.emit())
        worker.signals.speaking_finished.connect(lambda: signals.speaking_finished.emit())
        self.thread_pool.start(worker)

    @Slot()
    def _on_voice_button_clicked(self):
        self.audio_thread.start_listening()

    @Slot(str)
    def _on_speech_recognized(self, text: str):
        self._on_text_submitted(text)

    @Slot(bool)
    def _on_listening_state_changed(self, is_listening: bool):
        self.input_zone.on_listening_state_changed(is_listening)
        self.status_bar.set_mic_status(is_listening)

    @Slot(str)
    def _on_audio_error(self, error: str):
        self.input_zone.on_listening_state_changed(False)
        self.status_bar.set_mic_status(False)
        if "timeout" not in error.lower():
            self.chat_widget.add_message("System", f"Audio: {error}")

    @Slot(str, str)
    def _on_quick_action(self, action_id: str, command: str):
        self.chat_widget.add_message("You", f"[Quick Action: {action_id}]")
        self.chat_widget.show_typing()
        self.input_zone.set_enabled(False)
        self.quick_actions.highlight_tile(action_id, True)

        worker = QuickActionWorker(action_id, command)
        worker.signals.finished.connect(lambda response: self._on_quick_action_finished(action_id, response))
        worker.signals.error.connect(self._on_command_error)
        self.thread_pool.start(worker)

    @Slot(str, str)
    def _on_response_ready(self, sender: str, response: str):
        self.chat_widget.hide_typing()
        self.chat_widget.add_message(sender, response)
        self.input_zone.set_enabled(True)
        self.input_zone.focus_input()

    @Slot(str)
    def _on_command_finished(self, response: str):
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("A.L.F.R.E.D", response)
        self.input_zone.set_enabled(True)
        self.input_zone.focus_input()
        signals.llm_status_changed.emit("Claude 3.5 Sonnet", True)
        if "powering down" in response.lower():
            self.close()

    @Slot(str, str)
    def _on_quick_action_finished(self, action_id: str, response: str):
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("A.L.F.R.E.D", response)
        self.input_zone.set_enabled(True)
        self.quick_actions.highlight_tile(action_id, False)

    @Slot(str)
    def _on_command_error(self, error: str):
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("System", f"Error: {error}")
        self.input_zone.set_enabled(True)
        self.input_zone.focus_input()
        signals.llm_status_changed.emit("Disconnected", False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._size_grip.move(
            self.width() - self._size_grip.width() - 4,
            self.height() - self._size_grip.height() - 4,
        )

    def closeEvent(self, event):
        self.system_monitor_thread.stop()
        self.audio_thread.stop()
        self.thread_pool.waitForDone(3000)
        event.accept()
