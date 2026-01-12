"""
Command processing worker for handling ALFRED commands in a thread pool.
"""
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Signals for the command worker."""

    started = Signal()                    # Emitted when processing starts
    finished = Signal(str)                # Emitted with response text
    error = Signal(str)                   # Emitted with error message
    speaking_started = Signal()           # Emitted when TTS begins
    speaking_finished = Signal()          # Emitted when TTS ends
    progress = Signal(str)                # Emitted for progress updates


class CommandWorker(QRunnable):
    """
    Worker for processing ALFRED commands in a thread pool.
    Uses QRunnable for efficient thread pool execution.
    """

    def __init__(self, command: str, speak_response: bool = True):
        """
        Initialize the command worker.

        Args:
            command: The command text to process
            speak_response: Whether to speak the response via TTS
        """
        super().__init__()
        self.command = command
        self.speak_response = speak_response
        self.signals = WorkerSignals()
        self._is_cancelled = False

    @Slot()
    def run(self):
        """Execute the command processing."""
        self.signals.started.emit()

        try:
            # Import here to avoid circular imports
            from core.brain import get_response
            from services.automation import run_command

            # Check for shutdown command first
            if "shutdown" in self.command.lower():
                self.signals.finished.emit("Powering down.")
                return

            # Try system automation command first
            system_response = run_command(self.command)
            if system_response:
                response = system_response
            else:
                # Fall back to AI response
                response = get_response(self.command)

            # Handle cancelled state
            if self._is_cancelled:
                return

            # Emit response first (shows text in chat)
            self.signals.finished.emit(response)

            # Then speak the response
            if self.speak_response and response:
                self._speak_response(response)

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.signals.error.emit(error_msg)
            self.signals.finished.emit(f"I encountered an error: {str(e)}")

    def _speak_response(self, response: str):
        """Speak the response using TTS."""
        try:
            self.signals.speaking_started.emit()

            # Import voice module
            from core.voice import speak
            speak(response)

            self.signals.speaking_finished.emit()
        except Exception as e:
            self.signals.error.emit(f"TTS error: {str(e)}")
            self.signals.speaking_finished.emit()

    def cancel(self):
        """Cancel the worker (best effort)."""
        self._is_cancelled = True


class QuickActionWorker(QRunnable):
    """
    Worker specifically for quick action commands.
    Similar to CommandWorker but with action-specific handling.
    """

    def __init__(self, action_id: str, command: str):
        """
        Initialize the quick action worker.

        Args:
            action_id: The action identifier
            command: The command to execute
        """
        super().__init__()
        self.action_id = action_id
        self.command = command
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """Execute the quick action."""
        self.signals.started.emit()
        self.signals.progress.emit(f"Executing {self.action_id}...")

        try:
            # Import here to avoid circular imports
            from core.brain import get_response
            from services.automation import run_command

            # Try automation command first
            response = run_command(self.command)

            if not response:
                # Fall back to brain
                response = get_response(self.command)

            # Emit response first (shows text in chat)
            self.signals.finished.emit(response)

            # Then speak the response
            try:
                self.signals.speaking_started.emit()
                from core.voice import speak
                speak(response)
                self.signals.speaking_finished.emit()
            except Exception:
                self.signals.speaking_finished.emit()

        except Exception as e:
            error_msg = f"Quick action error: {str(e)}"
            self.signals.error.emit(error_msg)
            self.signals.finished.emit(f"Failed to execute {self.action_id}")
