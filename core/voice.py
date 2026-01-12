import pyttsx3
import numpy as np
from elevenlabs import ElevenLabs, play, VoiceSettings
from config import ELEVENLABS_KEY, ALFRED_VOICE_ID, VOICE_RATE

# Flag to track if GUI signals are available
_gui_signals_available = False
_gui_signals = None

def _init_gui_signals():
    """Initialize GUI signals if available."""
    global _gui_signals_available, _gui_signals
    try:
        from ui.signals import signals
        _gui_signals = signals
        _gui_signals_available = True
    except ImportError:
        _gui_signals_available = False


def _emit_audio_data(audio_bytes):
    """Emit audio data to GUI for waveform visualization."""
    global _gui_signals_available, _gui_signals
    if not _gui_signals_available:
        _init_gui_signals()

    if _gui_signals_available and _gui_signals:
        try:
            # Convert bytes to numpy array for visualization
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            _gui_signals.output_audio_data.emit(audio_array)
        except Exception:
            pass  # Silently ignore visualization errors

# Initialize ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_KEY and ALFRED_VOICE_ID:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_KEY)

# Initialize pyttsx3 as offline fallback
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', VOICE_RATE)


def speak_with_pyttsx3(text):
    """Offline TTS fallback using pyttsx3."""
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
        return True
    except Exception as e:
        print(f"[pyttsx3 error] {e}")
        return False


def speak(text):
    print(f"A.L.F.R.E.D: {text}")

    # Emit speaking started signal if GUI is available
    global _gui_signals_available, _gui_signals
    if not _gui_signals_available:
        _init_gui_signals()
    if _gui_signals_available and _gui_signals:
        try:
            _gui_signals.speaking_started.emit()
        except Exception:
            pass

    # Try ElevenLabs first (premium voice)
    if elevenlabs_client:
        try:
            audio = elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=ALFRED_VOICE_ID,
                model_id="eleven_turbo_v2_5",  # Updated model (free tier compatible)
                voice_settings=VoiceSettings(
                    stability=0.4,
                    similarity_boost=0.75
                )
            )

            # Play audio directly - play() handles the generator
            play(audio)

            # Emit speaking finished signal
            _emit_speaking_finished()
            return
        except Exception as e:
            print(f"[ElevenLabs failed] {e}")

    # Fallback to pyttsx3 (offline)
    if speak_with_pyttsx3(text):
        _emit_speaking_finished()
        return

    # Final fallback: text only
    print(f"A.L.F.R.E.D (text-only): {text}")
    _emit_speaking_finished()


def _emit_speaking_finished():
    """Emit speaking finished signal if GUI is available."""
    global _gui_signals_available, _gui_signals
    if _gui_signals_available and _gui_signals:
        try:
            _gui_signals.speaking_finished.emit()
        except Exception:
            pass
