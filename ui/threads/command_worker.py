"""
Command processing worker for handling ALFRED commands in a thread pool.
"""
from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from utils.logger import get_logger

logger = get_logger(__name__)


class WorkerSignals(QObject):
    """Signals for the command worker."""

    started = Signal()                    # Emitted when processing starts
    finished = Signal(str)                # Emitted with response text
    error = Signal(str)                   # Emitted with error message
    speaking_started = Signal()           # Emitted when TTS begins
    speaking_finished = Signal()          # Emitted when TTS ends
    progress = Signal(str)                # Emitted for progress updates


def execute_command(command: str) -> str:
    """
    Execute a command through automation or AI fallback.

    Args:
        command: The command text to process

    Returns:
        Response string from the command execution
    """
    # Import here to avoid circular imports
    from core.brain import get_response
    from services.automation import run_command

    # Try automation command first
    response = run_command(command)
    if response:
        return response

    # Fall back to AI response
    return get_response(command)


def speak_with_signals(response: str, signals: WorkerSignals):
    """
    Speak a response and emit appropriate signals.

    Args:
        response: Text to speak
        signals: WorkerSignals instance for emitting TTS state
    """
    try:
        signals.speaking_started.emit()
        from core.voice import speak
        speak(response)
        signals.speaking_finished.emit()
    except (OSError, RuntimeError, ImportError) as e:
        logger.warning(f"TTS failed: {e}")
        signals.speaking_finished.emit()


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
            # Check for shutdown command first
            if "shutdown" in self.command.lower():
                self.signals.finished.emit("Powering down.")
                return

            response = execute_command(self.command)

            # Handle cancelled state
            if self._is_cancelled:
                return

            # Emit response first (shows text in chat)
            self.signals.finished.emit(response)

            # Then speak the response
            if self.speak_response and response:
                speak_with_signals(response, self.signals)

        except Exception as e:
            logger.error(f"Command processing error: {e}", exc_info=True)
            self.signals.error.emit(f"Error processing command: {str(e)}")
            self.signals.finished.emit(f"I encountered an error: {str(e)}")

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
            response = execute_command(self.command)

            # Emit response first (shows text in chat)
            self.signals.finished.emit(response)

            # Then speak the response
            speak_with_signals(response, self.signals)

        except Exception as e:
            logger.error(f"Quick action error ({self.action_id}): {e}", exc_info=True)
            self.signals.error.emit(f"Quick action error: {str(e)}")
            self.signals.finished.emit(f"Failed to execute {self.action_id}")
