"""
Core brain module for A.L.F.R.E.D - handles command routing and LLM interactions.
"""
from __future__ import annotations

import threading
from typing import Optional

from openai import OpenAI
from config import OPENAI_KEY, OPENROUTER_API_KEY
from memory.memory_manager import remember, recall, forget, list_memory, semantic_search_memory
from services.automation import run_command
from service_commands.calendar_commands import handle_calendar_command
from service_commands.weather_commands import handle_weather_command
from service_commands.file_assistant_commands import handle_file_command
from service_commands.system_monitor_commands import handle_system_monitor_command
from service_commands.memory_commands import handle_memory_commands
from utils.logger import get_logger

logger = get_logger(__name__)

client: OpenAI = OpenAI(api_key=OPENAI_KEY)

# Thread-safe conversation history
_history_lock: threading.Lock = threading.Lock()
_conversation_history: list[dict[str, str]] = []
MAX_HISTORY: int = 10

SYSTEM_PROMPT = """You are A.L.F.R.E.D, an All Knowing Logical Facilitator for Reasoned Execution of Duties.
You are a sophisticated AI assistant inspired by J.A.R.V.I.S. Be helpful, concise, and maintain a professional yet friendly demeanor.
Address the user respectfully and provide accurate, thoughtful responses."""


def add_to_history(role: str, content: str) -> None:
    """Add a message to conversation history, maintaining max size (thread-safe)."""
    with _history_lock:
        _conversation_history.append({"role": role, "content": content})
        # Trim history more efficiently - remove oldest pair if over limit
        while len(_conversation_history) > MAX_HISTORY * 2:
            _conversation_history.pop(0)


def get_response(text: str) -> str:
    """
    Process user input and return appropriate response.

    Routes through memory commands, service commands, system commands,
    then falls back to LLM query.
    """
    lower: str = text.lower().strip()

    try:
        # Memory Commands
        response: Optional[str] = handle_memory_commands(lower)
        if response:
            return response

        # Service Commands
        response = handle_service_commands(lower)
        if response:
            return response

        # System Level OS Commands
        response = run_command(lower)
        if response:
            return response

        # General GPT Query with LLM fallback and conversation context
        add_to_history("user", text)
        response = query_llm_with_context(text)
        add_to_history("assistant", response)
        return response

    except Exception as e:
        logger.error(f"Error in get_response: {e}", exc_info=True)
        return "Sorry, I encountered an error while processing your request."


def handle_service_commands(text: str) -> Optional[str]:
    """Route text to appropriate service command handler."""
    if any(keyword in text for keyword in ["calendar", "schedule", "remind", "event"]):
        return handle_calendar_command(text)

    if any(keyword in text for keyword in ["weather", "forecast", "temperature"]):
        return handle_weather_command(text)

    if any(keyword in text for keyword in ["file", "document", "upload", "download"]):
        return handle_file_command(text)

    if any(keyword in text for keyword in ["system", "monitor", "status"]):
        return handle_system_monitor_command(text)

    return None


def build_messages() -> list[dict[str, str]]:
    """Build messages list with system prompt and conversation history (thread-safe)."""
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    with _history_lock:
        messages.extend(_conversation_history.copy())
    return messages


def query_llm_with_context(text: str) -> str:
    """Query LLM with conversation context and fallback support."""
    messages: list[dict[str, str]] = build_messages()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return completion.choices[0].message.content

    except Exception as e:
        logger.warning(f"Primary LLM (GPT-4o-mini) failed: {e}")
        # Fallback to OpenRouter
        try:
            openrouter_client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            completion = openrouter_client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=messages
            )
            logger.info("Successfully used fallback LLM (Claude via OpenRouter)")
            return completion.choices[0].message.content

        except Exception as fallback_error:
            logger.error(f"Fallback LLM also failed: {fallback_error}")
            return "Sorry, I couldn't process your request with any available models."
