"""
Audio capture thread for microphone input and waveform visualization.
"""
import numpy as np
from PySide6.QtCore import QThread, Signal

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


class AudioCaptureThread(QThread):
    """Thread for capturing microphone audio and speech recognition."""

    # Signals
    audio_chunk = Signal(object)           # np.ndarray of audio samples
    speech_recognized = Signal(str)        # Recognized speech text
    listening_state_changed = Signal(bool) # True when listening, False when stopped
    error_occurred = Signal(str)           # Error message

    # Audio parameters
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 16000
    CHANNELS = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._listening = False
        self._should_listen = False  # Flag to trigger listening

        if SR_AVAILABLE:
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.energy_threshold = 300
        else:
            self._recognizer = None

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

        try:
            p = pyaudio.PyAudio()

            # Open stream for waveform visualization
            viz_stream = p.open(
                format=pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )

            while self._running:
                try:
                    # Always capture audio for visualization
                    data = viz_stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                    self.audio_chunk.emit(audio_array)

                    # Check if we should start listening for speech
                    if self._should_listen and not self._listening:
                        self._listening = True
                        self._should_listen = False
                        self.listening_state_changed.emit(True)

                        # Stop viz stream temporarily
                        viz_stream.stop_stream()

                        # Do speech recognition
                        self._do_speech_recognition()

                        # Resume viz stream
                        viz_stream.start_stream()

                        self._listening = False
                        self.listening_state_changed.emit(False)

                except Exception as e:
                    if self._running:  # Only emit error if we're still supposed to be running
                        self.error_occurred.emit(f"Audio error: {str(e)}")

            # Cleanup
            viz_stream.stop_stream()
            viz_stream.close()
            p.terminate()

        except Exception as e:
            self.error_occurred.emit(f"Audio initialization error: {str(e)}")

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
                        self.speech_recognized.emit(text)

                except sr.WaitTimeoutError:
                    self.error_occurred.emit("No speech detected (timeout)")
                except sr.UnknownValueError:
                    self.error_occurred.emit("Could not understand audio")
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Speech service error: {str(e)}")

        except Exception as e:
            self.error_occurred.emit(f"Microphone error: {str(e)}")

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
            except Exception:
                pass
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
