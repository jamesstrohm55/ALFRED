"""
Voice synthesis module for A.L.F.R.E.D - handles text-to-speech with ElevenLabs and pyttsx3 fallback.

Uses lazy initialization to improve startup time.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import numpy as np
from numpy.typing import NDArray
from config import ELEVENLABS_KEY, ALFRED_VOICE_ID, VOICE_RATE
from utils.logger import get_logger

if TYPE_CHECKING:
    import pyttsx3
    from elevenlabs import ElevenLabs
    from ui.signals import GlobalSignals

logger = get_logger(__name__)

# Flag to track if GUI signals are available
_gui_signals_available: bool = False
_gui_signals: Optional[GlobalSignals] = None

# Lazy-initialized TTS engines
_elevenlabs_client: Optional[ElevenLabs] = None
_elevenlabs_initialized: bool = False
_tts_engine: Optional[pyttsx3.Engine] = None
_tts_initialized: bool = False


def _get_elevenlabs_client() -> Optional[ElevenLabs]:
    """Lazy initialization of ElevenLabs client."""
    global _elevenlabs_client, _elevenlabs_initialized

    if _elevenlabs_initialized:
        return _elevenlabs_client

    _elevenlabs_initialized = True

    if ELEVENLABS_KEY and ALFRED_VOICE_ID:
        try:
            from elevenlabs import ElevenLabs
            _elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_KEY)
            logger.debug("ElevenLabs client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize ElevenLabs: {e}")
            _elevenlabs_client = None

    return _elevenlabs_client


def _get_tts_engine() -> Optional[pyttsx3.Engine]:
    """Lazy initialization of pyttsx3 TTS engine."""
    global _tts_engine, _tts_initialized

    if _tts_initialized:
        return _tts_engine

    _tts_initialized = True

    try:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty('rate', VOICE_RATE)
        logger.debug("pyttsx3 engine initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize pyttsx3: {e}")
        _tts_engine = None

    return _tts_engine


def _init_gui_signals() -> None:
    """Initialize GUI signals if available."""
    global _gui_signals_available, _gui_signals
    try:
        from ui.signals import signals
        _gui_signals = signals
        _gui_signals_available = True
    except ImportError:
        _gui_signals_available = False


def _emit_audio_data(audio_bytes: bytes) -> None:
    """Emit audio data to GUI for waveform visualization."""
    global _gui_signals_available, _gui_signals
    if not _gui_signals_available:
        _init_gui_signals()

    if _gui_signals_available and _gui_signals:
        try:
            # Convert bytes to numpy array for visualization
            audio_array: NDArray[np.float32] = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            _gui_signals.output_audio_data.emit(audio_array)
        except (ValueError, RuntimeError) as e:
            # Visualization errors are non-critical, log at debug level
            logger.debug(f"Audio visualization error: {e}")


def speak_with_pyttsx3(text: str) -> bool:
    """Offline TTS fallback using pyttsx3."""
    engine = _get_tts_engine()
    if engine is None:
        return False

    try:
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[pyttsx3 error] {e}")
        return False


def speak(text: str) -> None:
    """
    Speak text using available TTS engine.

    Tries ElevenLabs first, falls back to pyttsx3, then text-only output.
    Uses lazy initialization for faster startup.
    """
    print(f"A.L.F.R.E.D: {text}")

    # Emit speaking started signal if GUI is available
    global _gui_signals_available, _gui_signals
    if not _gui_signals_available:
        _init_gui_signals()
    if _gui_signals_available and _gui_signals:
        try:
            _gui_signals.speaking_started.emit()
        except RuntimeError as e:
            logger.debug(f"Could not emit speaking_started signal: {e}")

    # Try ElevenLabs first (premium voice)
    elevenlabs_client = _get_elevenlabs_client()
    if elevenlabs_client:
        try:
            from elevenlabs import play, VoiceSettings

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


def _emit_speaking_finished() -> None:
    """Emit speaking finished signal if GUI is available."""
    global _gui_signals_available, _gui_signals
    if _gui_signals_available and _gui_signals:
        try:
            _gui_signals.speaking_finished.emit()
        except RuntimeError as e:
            logger.debug(f"Could not emit speaking_finished signal: {e}")
