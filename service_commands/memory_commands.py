"""
Memory command handler for A.L.F.R.E.D - processes remember/recall/forget commands.
"""
from __future__ import annotations

from typing import Any, Optional

from memory.memory_manager import remember, recall, forget, list_memory, load_memory, save_memory


def initialize_memory() -> None:
    """Ensure memory file exists and is loaded."""
    load_memory()  # Load memory to ensure the file exists


def handle_memory_commands(text: str) -> Optional[str]:
    """
    Handle memory-related commands (remember, recall, forget, list).

    Args:
        text: The user's command text

    Returns:
        Response string or None if not a memory command
    """
    lower: str = text.lower().strip()

    if lower.startswith("remember that"):
        _, fact = lower.split("remember that", 1)
        if " is " in fact:
            key, value = fact.split(" is ", 1)
            remember(key.strip(), value.strip())
            key_for_reply: str = key.strip().replace("my ", "your ")
            return f"I'll remember that {key_for_reply} is {value.strip()}."
        return "Please phrase it like: 'Remember that [key] is [value]'."

    if "what do you remember about" in lower or "what do you know about" in lower:
        key = lower.replace("what do you remember about", "").replace("what do you know about", "").strip()
        key_for_reply = key.replace("my ", "your ")
        value: Optional[str] = recall(key)
        return f"{key_for_reply.capitalize()} is {value}." if value else f"I don't remember anything about {key_for_reply}."

    if lower.startswith("forget"):
        key = lower.replace("forget", "").strip()
        success: bool = forget(key)
        if success:
            return f"I've forgotten everything about {key}."
        else:
            return f"I don't remember anything about {key} to forget."

    if "what do you remember" in lower or "list everything you remember" in lower:
        data: dict[str, Any] = list_memory()
        return "I don't have anything stored yet." if not data else "Here is what I remember:\n" + "\n".join([f"{k}: {v}" for k, v in data.items()])

    return None
