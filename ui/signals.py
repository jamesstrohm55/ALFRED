"""
Global Qt signals for cross-component communication in ALFRED.
Uses PySide6's Signal system for thread-safe UI updates.
"""
from PySide6.QtCore import QObject, Signal


class ALFREDSignals(QObject):
    """Global signals for cross-component communication."""

    # Command processing
    command_received = Signal(str)              # Raw command text
    response_ready = Signal(str, str)           # sender, response

    # Voice/Audio states
    listening_started = Signal()
    listening_stopped = Signal()
    speech_recognized = Signal(str)             # recognized text
    speaking_started = Signal()
    speaking_finished = Signal()

    # Audio visualization data (use object type for numpy arrays)
    input_audio_data = Signal(object)           # np.ndarray from mic
    output_audio_data = Signal(object)          # np.ndarray from TTS

    # System monitoring
    system_stats = Signal(dict)                 # system stats dictionary

    # Quick actions
    action_triggered = Signal(str)              # action_name

    # UI state
    ui_busy = Signal(bool)                      # Show/hide loading state

    # Error handling
    error_occurred = Signal(str)                # error message


# Global singleton instance for application-wide signal access
signals = ALFREDSignals()
