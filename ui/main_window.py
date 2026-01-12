"""
Main window for the ALFRED GUI application.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QFrame, QApplication
)
from PySide6.QtCore import Qt, Slot, QThreadPool
from PySide6.QtGui import QFont

from ui.styles.colors import COLORS
from ui.styles.dark_theme import DARK_THEME_QSS
from ui.signals import signals

from ui.widgets.chat_widget import ChatWidget
from ui.widgets.input_bar import InputBar
from ui.widgets.waveform_widget import DualWaveformWidget
from ui.widgets.system_dashboard import SystemDashboard
from ui.widgets.quick_actions import QuickActionsWidget

from ui.threads.system_monitor_thread import SystemMonitorThread
from ui.threads.audio_thread import AudioCaptureThread
from ui.threads.command_worker import CommandWorker, QuickActionWorker


class MainWindow(QMainWindow):
    """Main application window for ALFRED."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._setup_threads()
        self._connect_signals()

        # Show welcome message
        self.chat_widget.add_message(
            "A.L.F.R.E.D",
            "Hello! I'm A.L.F.R.E.D, your personal assistant. How can I help you today?"
        )

    def _setup_window(self):
        """Configure the main window."""
        self.setWindowTitle("A.L.F.R.E.D")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Apply dark theme
        self.setStyleSheet(DARK_THEME_QSS)

    def _setup_ui(self):
        """Set up the main UI layout."""
        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Left panel (sidebar with dashboard and quick actions)
        left_panel = self._create_left_panel()

        # Right panel (chat area)
        right_panel = self._create_right_panel()

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])  # Initial sizes
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Right panel stretches

        main_layout.addWidget(splitter)

    def _create_left_panel(self) -> QWidget:
        """Create the left sidebar panel."""
        panel = QWidget()
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(450)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # System dashboard
        self.system_dashboard = SystemDashboard()

        # Quick actions
        self.quick_actions = QuickActionsWidget()

        layout.addWidget(self.system_dashboard)
        layout.addWidget(self.quick_actions)
        layout.addStretch()

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the right chat panel."""
        panel = QWidget()

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Chat widget
        self.chat_widget = ChatWidget()

        # Waveform widget
        self.waveform_widget = DualWaveformWidget()

        # Input bar
        self.input_bar = InputBar()

        layout.addWidget(self.chat_widget, stretch=1)
        layout.addWidget(self.waveform_widget)
        layout.addWidget(self.input_bar)

        return panel

    def _setup_threads(self):
        """Initialize background threads."""
        # Thread pool for command workers
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)

        # System monitor thread
        self.system_monitor_thread = SystemMonitorThread(interval_ms=1000)
        self.system_monitor_thread.stats_updated.connect(self.system_dashboard.update_stats)
        self.system_monitor_thread.start()

        # Audio capture thread
        self.audio_thread = AudioCaptureThread()
        self.audio_thread.audio_chunk.connect(self.waveform_widget.update_input)
        self.audio_thread.speech_recognized.connect(self._on_speech_recognized)
        self.audio_thread.listening_state_changed.connect(self._on_listening_state_changed)
        self.audio_thread.error_occurred.connect(self._on_audio_error)
        self.audio_thread.start()

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Input bar signals
        self.input_bar.text_submitted.connect(self._on_text_submitted)
        self.input_bar.voice_button_clicked.connect(self._on_voice_button_clicked)

        # Quick actions signals
        self.quick_actions.action_triggered.connect(self._on_quick_action)

        # Global signals
        signals.response_ready.connect(self._on_response_ready)
        signals.output_audio_data.connect(self.waveform_widget.update_output)

        # Speaking signals for output waveform animation
        signals.speaking_started.connect(self.waveform_widget.start_output_simulation)
        signals.speaking_finished.connect(self.waveform_widget.stop_output_simulation)

    @Slot(str)
    def _on_text_submitted(self, text: str):
        """Handle text input submission."""
        if not text.strip():
            return

        # Add user message to chat
        self.chat_widget.add_message("You", text)

        # Show typing indicator
        self.chat_widget.show_typing()

        # Disable input while processing
        self.input_bar.set_enabled(False)

        # Process command in thread pool
        worker = CommandWorker(text)
        worker.signals.finished.connect(self._on_command_finished)
        worker.signals.error.connect(self._on_command_error)
        worker.signals.speaking_started.connect(lambda: signals.speaking_started.emit())
        worker.signals.speaking_finished.connect(lambda: signals.speaking_finished.emit())

        self.thread_pool.start(worker)

    @Slot()
    def _on_voice_button_clicked(self):
        """Handle voice button click - start listening."""
        self.audio_thread.start_listening()

    @Slot(str)
    def _on_speech_recognized(self, text: str):
        """Handle recognized speech."""
        # Process the recognized text
        self._on_text_submitted(text)

    @Slot(bool)
    def _on_listening_state_changed(self, is_listening: bool):
        """Handle listening state changes."""
        self.input_bar.set_listening_state(is_listening)
        if is_listening:
            self.input_bar.set_placeholder("Listening... Speak now")
            self.waveform_widget.input_waveform.set_active(True)
        else:
            self.input_bar.set_placeholder("Type your message here...")
            self.waveform_widget.input_waveform.set_active(False)

    @Slot(str)
    def _on_audio_error(self, error: str):
        """Handle audio errors."""
        # Reset listening state
        self.input_bar.set_listening_state(False)
        self.input_bar.set_placeholder("Type your message here...")
        # Only show significant errors in chat (not timeouts)
        if "timeout" not in error.lower():
            self.chat_widget.add_message("System", f"Audio: {error}")

    @Slot(str, str)
    def _on_quick_action(self, action_id: str, command: str):
        """Handle quick action button click."""
        # Add user action to chat
        self.chat_widget.add_message("You", f"[Quick Action: {action_id}]")

        # Show typing indicator
        self.chat_widget.show_typing()

        # Disable input
        self.input_bar.set_enabled(False)

        # Highlight the tile
        self.quick_actions.highlight_tile(action_id, True)

        # Process action in thread pool
        worker = QuickActionWorker(action_id, command)
        worker.signals.finished.connect(
            lambda response: self._on_quick_action_finished(action_id, response)
        )
        worker.signals.error.connect(self._on_command_error)

        self.thread_pool.start(worker)

    @Slot(str, str)
    def _on_response_ready(self, sender: str, response: str):
        """Handle response from global signals."""
        self.chat_widget.hide_typing()
        self.chat_widget.add_message(sender, response)
        self.input_bar.set_enabled(True)
        self.input_bar.focus_input()

    @Slot(str)
    def _on_command_finished(self, response: str):
        """Handle command completion."""
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("A.L.F.R.E.D", response)
        self.input_bar.set_enabled(True)
        self.input_bar.focus_input()

        # Check for shutdown
        if "powering down" in response.lower():
            self.close()

    @Slot(str, str)
    def _on_quick_action_finished(self, action_id: str, response: str):
        """Handle quick action completion."""
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("A.L.F.R.E.D", response)
        self.input_bar.set_enabled(True)

        # Remove highlight
        self.quick_actions.highlight_tile(action_id, False)

    @Slot(str)
    def _on_command_error(self, error: str):
        """Handle command errors."""
        self.chat_widget.hide_typing()
        self.chat_widget.add_message("System", f"Error: {error}")
        self.input_bar.set_enabled(True)
        self.input_bar.focus_input()

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop threads
        self.system_monitor_thread.stop()
        self.audio_thread.stop()

        # Wait for thread pool
        self.thread_pool.waitForDone(3000)

        # Accept the close event
        event.accept()
