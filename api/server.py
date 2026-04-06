"""FastAPI application for A.L.F.R.E.D — thin HTTP layer over existing logic."""

from __future__ import annotations

import asyncio
import json
import uuid

from fastapi import Depends, FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.auth import check_rate_limit
from api.models import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    HealthResponse,
    MemoryCreateRequest,
    MemoryCreateResponse,
    MemoryDeleteResponse,
    MemoryListResponse,
    MemoryRecallResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
)
from core.brain import get_conversation_history, get_response
from memory.database import check_connection
from memory.memory_manager import forget, list_memory, recall, remember, semantic_search_memory

app = FastAPI(
    title="A.L.F.R.E.D API",
    description="All Knowing Logical Facilitator for Reasoned Execution of Duties",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Chat ──────────────────────────────────────────────────────────────────────


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request, user: dict | None = Depends(check_rate_limit)):
    session_id = req.session_id or str(uuid.uuid4())
    user_id = user["id"] if user else None

    # Store client IP so weather geolocation uses the caller's location, not the server's
    from services.weather_service import set_client_ip

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
    set_client_ip(client_ip)

    try:
        response = get_response(req.message, session_id=session_id, user_id=user_id)
    except Exception as e:
        return ChatResponse(response=f"Error processing request: {e}", session_id=session_id)
    return ChatResponse(response=response, session_id=session_id)


@app.get("/chat/history", response_model=ChatHistoryResponse)
def chat_history(
    limit: int = Query(default=10, ge=1, le=100),
    session_id: str | None = Query(default=None),
    user: dict | None = Depends(check_rate_limit),
):
    user_id = user["id"] if user else None
    history = get_conversation_history(limit=limit, session_id=session_id, user_id=user_id)
    messages = [ConversationMessage(role=m["role"], content=m["content"]) for m in history]
    return ChatHistoryResponse(messages=messages, session_id=session_id or "")


# ── Memory ────────────────────────────────────────────────────────────────────


@app.post("/memories", response_model=MemoryCreateResponse, status_code=201)
def create_memory(req: MemoryCreateRequest, _user: dict | None = Depends(check_rate_limit)):
    success = remember(key=req.key, value=req.value, category=req.category, tags=req.tags)
    message = f"Memory '{req.key}' stored successfully." if success else f"Failed to store memory '{req.key}'."
    return MemoryCreateResponse(success=success, key=req.key, message=message)


@app.get("/memories", response_model=MemoryListResponse)
def list_memories(category: str | None = Query(default=None), _user: dict | None = Depends(check_rate_limit)):
    memories = list_memory(category=category)
    return MemoryListResponse(memories=memories, count=len(memories), category=category)


@app.get("/memories/{key}", response_model=MemoryRecallResponse)
def recall_memory(key: str, _user: dict | None = Depends(check_rate_limit)):
    value = recall(key)
    return MemoryRecallResponse(key=key, value=value, found=value is not None)


@app.delete("/memories/{key}", response_model=MemoryDeleteResponse)
def delete_memory(key: str, _user: dict | None = Depends(check_rate_limit)):
    success = forget(key)
    message = f"Memory '{key}' deleted." if success else f"Memory '{key}' not found."
    return MemoryDeleteResponse(success=success, key=key, message=message)


@app.post("/memories/search", response_model=MemorySearchResponse)
def search_memories(req: MemorySearchRequest, _user: dict | None = Depends(check_rate_limit)):
    raw = semantic_search_memory(query=req.query, n_results=req.n_results)
    results = [MemorySearchResult(**r) for r in raw] if raw else []
    return MemorySearchResponse(results=results, query=req.query, count=len(results))


# ── System ────────────────────────────────────────────────────────────────────


@app.get("/system/health", response_model=HealthResponse)
def health():
    connected = check_connection()
    return HealthResponse(
        status="healthy" if connected else "degraded",
        supabase=connected,
        version="1.0.0",
    )


# ── WebSocket ─────────────────────────────────────────────────────────────────


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    # Validate API key from query param before accepting
    api_key = ws.query_params.get("api_key")
    if not api_key:
        await ws.close(code=4001, reason="Missing api_key query parameter")
        return

    from api.auth import _get_user

    user = _get_user(api_key)
    if not user:
        await ws.close(code=4001, reason="Invalid API key")
        return

    await ws.accept()
    session_id = str(uuid.uuid4())
    user_id = user["id"]

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)

            if payload.get("type") != "chat" or not payload.get("message"):
                await ws.send_json({"type": "error", "content": 'Expected {"type": "chat", "message": "..."}'})
                continue

            # Allow client to reuse session
            sid = payload.get("session_id") or session_id

            await ws.send_json({"type": "ack"})

            import functools

            loop = asyncio.get_event_loop()
            fn = functools.partial(get_response, payload["message"], session_id=sid, user_id=user_id)
            response = await loop.run_in_executor(None, fn)

            await ws.send_json({"type": "response", "content": response, "session_id": sid})
    except WebSocketDisconnect:
        pass
