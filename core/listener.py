"""
Listener module for A.L.F.R.E.D - handles speech recognition and text input fallback.
"""
from __future__ import annotations

from typing import Optional

import speech_recognition as sr


def listen() -> Optional[str]:
    """
    Listen for voice input or fall back to text input.

    Returns:
        The recognized command string, or None if recognition failed.
    """
    recognizer: sr.Recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio: sr.AudioData = recognizer.listen(source, timeout=5)
                command: str = recognizer.recognize_google(audio)
                print(f"You (via mic): {command}")
                return command
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                return None
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                return None
    except (OSError, AttributeError, IOError):
        # Mic not found, access issue, or audio stream error
        command = input("Microphone unavailable. Please type your command: ")
        print(f"You (typed): {command}")
        return command
