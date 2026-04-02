"""
Core brain module for A.L.F.R.E.D - handles command routing and LLM interactions.

Includes RAG (Retrieval-Augmented Generation) for injecting relevant memories
into LLM prompts, and Supabase-backed conversation persistence.
"""

from __future__ import annotations

import threading
import uuid

from openai import OpenAI

from config import OPENAI_KEY, OPENROUTER_API_KEY
from memory.database import get_supabase
from memory.memory_manager import get_recent_memories, semantic_search_memory
from service_commands.calendar_commands import handle_calendar_command
from service_commands.file_assistant_commands import handle_file_command
from service_commands.memory_commands import handle_memory_commands
from service_commands.system_monitor_commands import handle_system_monitor_command
from service_commands.weather_commands import handle_weather_command
from services.automation import run_command
from utils.logger import get_logger

logger = get_logger(__name__)

client: OpenAI = OpenAI(api_key=OPENAI_KEY)

# Session ID for this runtime — persisted conversations are grouped by session
SESSION_ID: str = str(uuid.uuid4())

# Thread lock for conversation DB writes
_history_lock: threading.Lock = threading.Lock()
MAX_HISTORY: int = 10

# Relevance threshold for RAG — higher similarity = more relevant
RAG_SIMILARITY_THRESHOLD: float = 0.5
RAG_MAX_TOKENS: int = 500

SYSTEM_PROMPT = (
    "You are A.L.F.R.E.D, an All Knowing Logical Facilitator for Reasoned Execution of Duties. "
    "You were created by James Strohm, a full-stack developer based in Belo Horizonte, Brazil. "
    "He built you from scratch using Python, FastAPI, Supabase, and pgvector, "
    "with a RAG pipeline, multi-provider LLM fallback chain, voice interface, "
    "and a PySide6 desktop GUI. You are his flagship project. "
    "You are a sophisticated AI assistant inspired by J.A.R.V.I.S. Be helpful, concise, "
    "and maintain a professional yet friendly demeanor. "
    "Address the user respectfully and provide accurate, thoughtful responses."
)


def add_to_history(role: str, content: str, session_id: str | None = None, user_id: str | None = None) -> None:
    """Persist a message to the conversations table in Supabase."""
    sid = session_id or SESSION_ID
    with _history_lock:
        try:
            sb = get_supabase()
            row: dict = {"session_id": sid, "role": role, "content": content}
            if user_id:
                row["user_id"] = user_id
            sb.table("conversations").insert(row).execute()
        except Exception as e:
            logger.error(f"Failed to persist conversation: {e}")


def get_conversation_history(
    limit: int | None = None, session_id: str | None = None, user_id: str | None = None
) -> list[dict[str, str]]:
    """
    Load recent conversation history from Supabase.

    For authenticated API users, history is scoped to that user and session only.
    For local/runtime usage without a user_id, it can fall back to a previous session
    for continuity across restarts.
    """
    sid = session_id or SESSION_ID
    effective_limit = (limit or MAX_HISTORY) * 2  # user+assistant pairs
    try:
        sb = get_supabase()

        # Try given session first
        query = sb.table("conversations").select("role, content")
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.eq("session_id", sid).order("timestamp", desc=True).limit(effective_limit).execute()

        rows = result.data
        if not rows and not user_id:
            # No messages in this session — load last few from any session
            result = (
                sb.table("conversations")
                .select("role, content")
                .neq("session_id", sid)
                .order("timestamp", desc=True)
                .limit(effective_limit)
                .execute()
            )
            rows = result.data

        # Rows come newest-first; reverse to chronological order
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
    except Exception as e:
        logger.error(f"Failed to load conversation history: {e}")
        return []


def _build_memory_context(text: str) -> str:
    """
    Build a RAG context string from semantic search and recent memories.

    Queries pgvector for semantically relevant memories and appends
    recent stored facts, filtering by similarity threshold.
    """
    context_parts: list[str] = []

    # Semantic search for relevant memories
    try:
        results = semantic_search_memory(text, n_results=5)
        if results:
            relevant = [r["document"] for r in results if r["similarity"] >= RAG_SIMILARITY_THRESHOLD]
            if relevant:
                context_parts.append("Semantically relevant memories:")
                for mem in relevant:
                    context_parts.append(f"  - {mem}")
    except Exception as e:
        logger.debug(f"Semantic search for RAG failed: {e}")

    # Recent stored facts
    try:
        recent = get_recent_memories(limit=5)
        if recent:
            context_parts.append("Recently stored facts:")
            for entry in recent:
                context_parts.append(f"  - {entry['key']}: {entry['value']}")
    except Exception as e:
        logger.debug(f"Recent memories for RAG failed: {e}")

    if not context_parts:
        return ""

    # Cap at approximate token limit (rough: 1 token ≈ 4 chars)
    context = "\n".join(context_parts)
    max_chars = RAG_MAX_TOKENS * 4
    if len(context) > max_chars:
        context = context[:max_chars] + "\n  ..."

    return context


def get_response(text: str, session_id: str | None = None, user_id: str | None = None) -> str:
    """
    Process user input and return appropriate response.

    Routes through memory commands, service commands, system commands,
    then falls back to LLM query.
    """
    lower: str = text.lower().strip()

    try:
        # Memory Commands
        response: str | None = handle_memory_commands(lower)
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
        add_to_history("user", text, session_id=session_id, user_id=user_id)
        response = query_llm_with_context(text, session_id=session_id, user_id=user_id)
        add_to_history("assistant", response, session_id=session_id, user_id=user_id)
        return response

    except Exception as e:
        logger.error(f"Error in get_response: {e}", exc_info=True)
        return "Sorry, I encountered an error while processing your request."


def handle_service_commands(text: str) -> str | None:
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


def build_messages(user_text: str, session_id: str | None = None, user_id: str | None = None) -> list[dict[str, str]]:
    """Build messages list with system prompt, RAG context, and conversation history."""
    # Build RAG-augmented system prompt
    memory_context = _build_memory_context(user_text)
    if memory_context:
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"## Relevant Memories\n"
            f"Use these memories to inform your response when relevant:\n\n"
            f"{memory_context}"
        )
    else:
        system_content = SYSTEM_PROMPT

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]

    # Load conversation history from Supabase
    history = get_conversation_history(session_id=session_id, user_id=user_id)
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    return messages


def query_llm_with_context(text: str, session_id: str | None = None, user_id: str | None = None) -> str:
    """Query LLM with conversation context, RAG memory injection, and fallback support."""
    messages: list[dict[str, str]] = build_messages(text, session_id=session_id, user_id=user_id)

    openrouter_client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

    # Try free-tier first to avoid burning credits
    try:
        completion = openrouter_client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free", messages=messages
        )
        return completion.choices[0].message.content
    except Exception as free_error:
        logger.warning(f"Free-tier LLM (Nemotron 30B) failed: {free_error}")

    try:
        completion = openrouter_client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=messages)
        return completion.choices[0].message.content
    except Exception as e:
        logger.warning(f"Primary LLM (Claude 3.5 Sonnet) failed: {e}")

    try:
        completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        logger.info("Successfully used fallback LLM (GPT-4o-mini)")
        return completion.choices[0].message.content
    except Exception as fallback_error:
        logger.error(f"Fallback LLM (GPT-4o-mini) also failed: {fallback_error}")
        return "Sorry, I couldn't process your request with any available models."
