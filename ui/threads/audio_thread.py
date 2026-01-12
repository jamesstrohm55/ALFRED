"""
Audio capture thread for microphone input and waveform visualization.

Optimizations:
- Visualization can be disabled to save CPU
- Larger chunk sizes when visualization is off
- Throttled signal emission to reduce overhead
"""
import numpy as np
from PySide6.QtCore import QThread, Signal
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not available - audio capture disabled")

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.warning("SpeechRecognition not available - voice input disabled")


class AudioCaptureThread(QThread):
    """
    Thread for capturing microphone audio and speech recognition.

    Can run in two modes:
    - Visualization mode: Continuous audio capture for waveform display
    - Listen-only mode: Only captures audio when speech recognition is requested
    """

    # Signals
    audio_chunk = Signal(object)           # np.ndarray of audio samples
    speech_recognized = Signal(str)        # Recognized speech text
    listening_state_changed = Signal(bool) # True when listening, False when stopped
    error_occurred = Signal(str)           # Error message

    # Audio parameters
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 16000
    CHANNELS = 1

    # Visualization throttling (emit every N chunks to reduce CPU)
    VIZ_EMIT_INTERVAL = 2  # Emit every 2nd chunk (~30 FPS at 16kHz)

    def __init__(self, parent=None, enable_visualization: bool = True):
        """
        Initialize the audio capture thread.

        Args:
            parent: Parent QObject
            enable_visualization: If True, continuously capture audio for waveform.
                                  If False, only capture when listening for speech.
        """
        super().__init__(parent)
        self._running = True
        self._listening = False
        self._should_listen = False
        self._visualization_enabled = enable_visualization
        self._viz_paused = False
        self._chunk_counter = 0

        if SR_AVAILABLE:
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.energy_threshold = 300
        else:
            self._recognizer = None

        logger.debug(f"AudioCaptureThread initialized (visualization={'on' if enable_visualization else 'off'})")

    def set_visualization_enabled(self, enabled: bool):
        """Enable or disable continuous audio visualization."""
        self._visualization_enabled = enabled
        logger.debug(f"Visualization {'enabled' if enabled else 'disabled'}")

    def pause_visualization(self):
        """Temporarily pause visualization (e.g., during TTS playback)."""
        self._viz_paused = True

    def resume_visualization(self):
        """Resume visualization after pause."""
        self._viz_paused = False

    def start_listening(self):
        """Start speech recognition mode."""
        self._should_listen = True

    def stop_listening(self):
        """Stop speech recognition mode (if possible)."""
        self._should_listen = False
        self._listening = False
        self.listening_state_changed.emit(False)

    def run(self):
        """Main audio capture loop."""
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio is not available")
            return

        if not SR_AVAILABLE:
            self.error_occurred.emit("Speech recognition is not available")
            return

        p = None
        viz_stream = None

        try:
            p = pyaudio.PyAudio()

            # Only open continuous stream if visualization is needed
            if self._visualization_enabled:
                viz_stream = p.open(
                    format=pyaudio.paInt16,
                    channels=self.CHANNELS,
                    rate=self.SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK_SIZE
                )
                logger.debug("Audio visualization stream opened")

            while self._running:
                try:
                    # Capture audio for visualization if enabled and not paused
                    if self._visualization_enabled and viz_stream and not self._viz_paused:
                        data = viz_stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

                        # Throttle emissions to reduce CPU overhead
                        self._chunk_counter += 1
                        if self._chunk_counter >= self.VIZ_EMIT_INTERVAL:
                            self._chunk_counter = 0
                            audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                            self.audio_chunk.emit(audio_array)
                    else:
                        # Sleep to prevent busy-waiting when not visualizing
                        self.msleep(50)

                    # Check if we should start listening for speech
                    if self._should_listen and not self._listening:
                        self._listening = True
                        self._should_listen = False
                        self.listening_state_changed.emit(True)

                        # Stop viz stream temporarily if running
                        if viz_stream:
                            viz_stream.stop_stream()

                        # Do speech recognition
                        self._do_speech_recognition()

                        # Resume viz stream if it was running
                        if viz_stream and self._visualization_enabled:
                            viz_stream.start_stream()

                        self._listening = False
                        self.listening_state_changed.emit(False)

                except Exception as e:
                    if self._running:
                        self.error_occurred.emit(f"Audio error: {str(e)}")
                        logger.warning(f"Audio capture error: {e}")

        except Exception as e:
            self.error_occurred.emit(f"Audio initialization error: {str(e)}")
            logger.error(f"Audio initialization failed: {e}")

        finally:
            # Cleanup
            if viz_stream:
                try:
                    viz_stream.stop_stream()
                    viz_stream.close()
                except Exception:
                    pass
            if p:
                try:
                    p.terminate()
                except Exception:
                    pass
            logger.debug("Audio capture thread stopped")

    def _do_speech_recognition(self):
        """Perform speech recognition using speech_recognition library."""
        try:
            with sr.Microphone(sample_rate=self.SAMPLE_RATE) as source:
                # Adjust for ambient noise briefly
                self._recognizer.adjust_for_ambient_noise(source, duration=0.3)

                # Listen for speech with timeout
                try:
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=10)

                    # Recognize with Google
                    text = self._recognizer.recognize_google(audio)
                    if text:
                        logger.debug(f"Speech recognized: {text}")
                        self.speech_recognized.emit(text)

                except sr.WaitTimeoutError:
                    self.error_occurred.emit("No speech detected (timeout)")
                except sr.UnknownValueError:
                    self.error_occurred.emit("Could not understand audio")
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Speech service error: {str(e)}")
                    logger.error(f"Speech recognition service error: {e}")

        except Exception as e:
            self.error_occurred.emit(f"Microphone error: {str(e)}")
            logger.error(f"Microphone access error: {e}")

    def stop(self):
        """Stop the audio capture thread."""
        self._running = False
        self._listening = False
        self._should_listen = False
        self.wait(3000)  # Wait up to 3 seconds


class AudioOutputMonitor(QThread):
    """Thread for monitoring TTS audio output."""

    audio_chunk = Signal(object)  # np.ndarray of audio samples

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._buffer = []

    def add_audio_data(self, audio_data):
        """Add audio data to be emitted for visualization."""
        if isinstance(audio_data, bytes):
            try:
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                self._buffer.append(audio_array)
            except ValueError as e:
                logger.debug(f"Could not convert audio data: {e}")
        elif isinstance(audio_data, np.ndarray):
            self._buffer.append(audio_data)

    def run(self):
        """Main loop for emitting buffered audio data."""
        while self._running:
            if self._buffer:
                audio_data = self._buffer.pop(0)
                self.audio_chunk.emit(audio_data)
            self.msleep(33)  # ~30 FPS

    def stop(self):
        """Stop the output monitor thread."""
        self._running = False
        self.wait()

    def clear_buffer(self):
        """Clear the audio buffer."""
        self._buffer = []
