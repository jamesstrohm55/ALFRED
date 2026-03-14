"""
Memory command handler for A.L.F.R.E.D - processes remember/recall/forget/search commands.
"""

from __future__ import annotations

import re
from typing import Any

from memory.memory_manager import (
    forget,
    list_memory,
    recall,
    remember,
    semantic_search_memory,
)


def _auto_categorize(key: str, value: str) -> str:
    """Heuristic auto-categorization based on key/value content."""
    text = f"{key} {value}".lower()
    if any(w in text for w in ["my ", "i am", "i'm"]):
        return "personal"
    if any(w in text for w in ["like", "prefer", "favorite", "favourite"]):
        return "preference"
    return "general"


def handle_memory_commands(text: str) -> str | None:
    """
    Handle memory-related commands (remember, recall, forget, list, search).

    Args:
        text: The user's command text (already lowered)

    Returns:
        Response string or None if not a memory command
    """
    lower: str = text.lower().strip()

    # Remember command
    if lower.startswith("remember that"):
        _, fact = lower.split("remember that", 1)
        if " is " in fact:
            key, value = fact.split(" is ", 1)
            key = key.strip()
            value = value.strip()
            category = _auto_categorize(key, value)
            remember(key, value, category=category)
            key_for_reply: str = key.replace("my ", "your ")
            return f"I'll remember that {key_for_reply} is {value}."
        return "Please phrase it like: 'Remember that [key] is [value]'."

    # Recall command
    if "what do you remember about" in lower or "what do you know about" in lower:
        key = lower.replace("what do you remember about", "").replace("what do you know about", "").strip()
        key_for_reply = key.replace("my ", "your ")
        value: str | None = recall(key)
        return (
            f"{key_for_reply.capitalize()} is {value}."
            if value
            else f"I don't remember anything about {key_for_reply}."
        )

    # Forget command
    if lower.startswith("forget"):
        key = lower.replace("forget", "").strip()
        success: bool = forget(key)
        if success:
            return f"I've forgotten everything about {key}."
        else:
            return f"I don't remember anything about {key} to forget."

    # Semantic search command
    if lower.startswith("search memory for") or lower.startswith("search memories for"):
        query = re.sub(r"^search\s+memor(?:y|ies)\s+for\s+", "", lower).strip()
        if not query:
            return "Please specify what to search for."
        results = semantic_search_memory(query, n_results=5)
        if not results:
            return f"No memories found matching '{query}'."
        lines = [f"Found {len(results)} relevant memories:"]
        for r in results:
            lines.append(f"  - {r['document']} (relevance: {r['similarity']:.0%})")
        return "\n".join(lines)

    # List memories — with optional category filter
    if (
        "what do you remember" in lower
        or "list everything you remember" in lower
        or re.match(r"list\s+\w+\s+memories", lower)
    ):
        # Check for category filter: "list personal memories", "list preference memories"
        cat_match = re.match(r"list\s+(\w+)\s+memories", lower)
        category = cat_match.group(1) if cat_match else None

        data: dict[str, Any] = list_memory(category=category)
        if not data:
            qualifier = f" {category}" if category else ""
            return f"I don't have any{qualifier} memories stored yet."
        header = f"Here are your {category} memories:" if category else "Here is what I remember:"
        return header + "\n" + "\n".join([f"  {k}: {v}" for k, v in data.items()])

    return None
