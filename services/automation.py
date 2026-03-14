"""
Automation service for A.L.F.R.E.D - handles system-level commands and OS integrations.
"""

from __future__ import annotations

import datetime
import difflib
import os
import webbrowser
from collections.abc import Callable

from config import MUSIC_PATH
from memory.database import get_supabase
from utils.logger import get_logger

logger = get_logger(__name__)

# === Individual Command Functions ===


def open_browser() -> str:
    """Open the default web browser to Google."""
    webbrowser.open("https://www.google.com")
    return "Opening your browser, sir."


def open_code() -> str:
    """Launch Visual Studio Code."""
    os.system("code")
    return "Launching Visual Studio Code."


def tell_time() -> str:
    """Return the current time formatted for speech."""
    now: datetime.datetime = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def play_music() -> str:
    """Play music from the configured music path."""
    if not MUSIC_PATH or not os.path.exists(MUSIC_PATH):
        return "Music path not configured. Please set MUSIC_PATH in your .env file."
    os.startfile(MUSIC_PATH)
    return "Playing your favorite track."


def lock_computer() -> str:
    """Lock the Windows workstation."""
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "Locking your computer, sir."


# === Command Registry: canonical command → function ===

command_map: dict[str, Callable[[], str]] = {
    "open browser": open_browser,
    "open vs code": open_code,
    "tell time": tell_time,
    "play music": play_music,
    "lock computer": lock_computer,
}

# === Fuzzy Matching Handler ===


def run_command(user_input: str) -> str | None:
    """
    Handle system-level commands (browser, VS Code, time, music, lock).

    Uses fuzzy matching to find the closest command match.
    """
    user_input = user_input.lower()
    phrases: list[str] = list(command_map.keys())

    # Log the raw input
    log_command(user_input)

    # Try to match to known system commands
    best_match: list[str] = difflib.get_close_matches(user_input, phrases, n=1, cutoff=0.5)
    if best_match:
        command: str = best_match[0]
        log_command(user_input, matched_command=command)
        return command_map[command]()

    return None


def log_command(input_text: str, matched_command: str | None = None) -> None:
    """Log command input and matched command to Supabase."""
    try:
        sb = get_supabase()
        sb.table("command_logs").insert(
            {
                "input_text": input_text,
                "matched_command": matched_command,
            }
        ).execute()
    except Exception as e:
        logger.warning(f"Failed to log command: {e}")
