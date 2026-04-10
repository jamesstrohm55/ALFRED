"""
Voice synthesis module for A.L.F.R.E.D - handles text-to-speech with ElevenLabs and pyttsx3 fallback.

Uses lazy initialization to improve startup time.
pyttsx3 on Windows requires COM STA — a dedicated TTSThread marshals all
background-thread calls through a single COM-initialized thread to prevent
crashes in Qt's MTA thread pool.
"""

from __future__ import annotations

import queue
import sys
import threading
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from config import ALFRED_VOICE_ID, ELEVENLABS_KEY, VOICE_RATE
from utils.logger import get_logger

if TYPE_CHECKING:
    from elevenlabs import ElevenLabs

    from ui.signals import GlobalSignals

logger = get_logger(__name__)

# ── GUI signal handles ─────────────────────────────────────────────────────────

_gui_signals_available: bool = False
_gui_signals: GlobalSignals | None = None

# ── ElevenLabs client ─────────────────────────────────────────────────────────

_elevenlabs_client: ElevenLabs | None = None
_elevenlabs_initialized: bool = False

# ── Dedicated TTS thread ──────────────────────────────────────────────────────
# pyttsx3 on Windows uses SAPI which requires COM STA.
# Qt's thread pool runs MTA threads — calling pyttsx3 from them crashes.
# The solution: own a single long-lived thread that initialises COM (STA),
# builds the pyttsx3 engine once, and serialises all speak requests.

_tts_queue: queue.Queue = queue.Queue()
_tts_thread: threading.Thread | None = None
_tts_thread_lock = threading.Lock()


def _tts_worker() -> None:
    """Dedicated TTS worker — initialises COM STA before touching pyttsx3."""
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.ole32.CoInitialize(None)
        except Exception as e:
            logger.debug(f"CoInitialize failed: {e}")

    engine = None
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", VOICE_RATE)
        logger.debug("pyttsx3 engine initialised in TTS thread")
    except Exception as e:
        logger.warning(f"pyttsx3 init failed in TTS thread: {e}")

    while True:
        item = _tts_queue.get()
        if item is None:
            break  # Shutdown signal

        text, done_event = item
        if engine is not None:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                logger.warning(f"pyttsx3 speak error: {e}")
        done_event.set()

    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.ole32.CoUninitialize()
        except Exception:
            pass


def _ensure_tts_thread() -> None:
    """Start the dedicated TTS thread if it's not running."""
    global _tts_thread
    with _tts_thread_lock:
        if _tts_thread is None or not _tts_thread.is_alive():
            _tts_thread = threading.Thread(target=_tts_worker, daemon=True, name="alfred-tts")
            _tts_thread.start()


# ── ElevenLabs ────────────────────────────────────────────────────────────────


def _get_elevenlabs_client() -> ElevenLabs | None:
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


def _speak_with_elevenlabs(text: str, elevenlabs_client: ElevenLabs) -> bool:
    """
    Speak text with ElevenLabs TTS via ffplay/ffmpeg.

    Returns True on success, False if ffplay is unavailable or playback fails.
    """
    import shutil

    try:
        has_ffplay = shutil.which("ffplay") is not None or shutil.which("ffmpeg") is not None
        if not has_ffplay:
            return False

        from elevenlabs import VoiceSettings, play

        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=ALFRED_VOICE_ID,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(stability=0.4, similarity_boost=0.75),
        )
        play(audio)
        return True
    except Exception as e:
        logger.warning(f"ElevenLabs TTS failed: {e}")
        return False


# ── GUI signals ───────────────────────────────────────────────────────────────


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
            audio_array: NDArray[np.float32] = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            _gui_signals.output_audio_data.emit(audio_array)
        except (ValueError, RuntimeError) as e:
            logger.debug(f"Audio visualization error: {e}")


def _emit_speaking_finished() -> None:
    """Emit speaking finished signal if GUI is available."""
    global _gui_signals_available, _gui_signals
    if _gui_signals_available and _gui_signals:
        try:
            _gui_signals.speaking_finished.emit()
        except RuntimeError as e:
            logger.debug(f"Could not emit speaking_finished signal: {e}")


# ── Public API ────────────────────────────────────────────────────────────────


def speak_with_pyttsx3(text: str) -> bool:
    """
    Offline TTS using pyttsx3.

    All calls are routed through a dedicated thread that owns the pyttsx3
    engine and has COM initialised in STA mode (required by SAPI on Windows).
    Blocks until speech completes.
    """
    try:
        _ensure_tts_thread()
        done = threading.Event()
        _tts_queue.put((text, done))
        done.wait(timeout=30)
        return True
    except Exception as e:
        logger.warning(f"pyttsx3 TTS queue error: {e}")
        return False


def speak(text: str) -> None:
    """
    Speak text using the best available TTS engine.

    Priority: ElevenLabs (if ffplay present) → pyttsx3 → text-only.
    Safe to call from any thread.
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

    # Try ElevenLabs first (premium voice, needs ffplay)
    elevenlabs_client = _get_elevenlabs_client()
    if elevenlabs_client and _speak_with_elevenlabs(text, elevenlabs_client):
        _emit_speaking_finished()
        return

    # Fallback: pyttsx3 via COM-safe dedicated thread
    if speak_with_pyttsx3(text):
        _emit_speaking_finished()
        return

    # Final fallback: text only (already printed above)
    _emit_speaking_finished()
