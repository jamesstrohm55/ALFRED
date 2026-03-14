"""FastAPI application for A.L.F.R.E.D — thin HTTP layer over existing logic."""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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
from core.brain import SESSION_ID, get_conversation_history, get_response
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
def chat(req: ChatRequest, request: Request):
    # Store client IP so weather geolocation uses the caller's location, not the server's
    from services.weather_service import set_client_ip

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
    set_client_ip(client_ip)

    try:
        response = get_response(req.message)
    except Exception as e:
        return ChatResponse(response=f"Error processing request: {e}", session_id=SESSION_ID)
    return ChatResponse(response=response, session_id=SESSION_ID)


@app.get("/chat/history", response_model=ChatHistoryResponse)
def chat_history(limit: int = Query(default=10, ge=1, le=100)):
    history = get_conversation_history(limit=limit)
    messages = [ConversationMessage(role=m["role"], content=m["content"]) for m in history]
    return ChatHistoryResponse(messages=messages, session_id=SESSION_ID)


# ── Memory ────────────────────────────────────────────────────────────────────


@app.post("/memories", response_model=MemoryCreateResponse, status_code=201)
def create_memory(req: MemoryCreateRequest):
    success = remember(key=req.key, value=req.value, category=req.category, tags=req.tags)
    message = f"Memory '{req.key}' stored successfully." if success else f"Failed to store memory '{req.key}'."
    return MemoryCreateResponse(success=success, key=req.key, message=message)


@app.get("/memories", response_model=MemoryListResponse)
def list_memories(category: str | None = Query(default=None)):
    memories = list_memory(category=category)
    return MemoryListResponse(memories=memories, count=len(memories), category=category)


@app.get("/memories/{key}", response_model=MemoryRecallResponse)
def recall_memory(key: str):
    value = recall(key)
    return MemoryRecallResponse(key=key, value=value, found=value is not None)


@app.delete("/memories/{key}", response_model=MemoryDeleteResponse)
def delete_memory(key: str):
    success = forget(key)
    message = f"Memory '{key}' deleted." if success else f"Memory '{key}' not found."
    return MemoryDeleteResponse(success=success, key=key, message=message)


@app.post("/memories/search", response_model=MemorySearchResponse)
def search_memories(req: MemorySearchRequest):
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
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)

            if payload.get("type") != "chat" or not payload.get("message"):
                await ws.send_json({"type": "error", "content": 'Expected {"type": "chat", "message": "..."}'})
                continue

            await ws.send_json({"type": "ack"})

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, get_response, payload["message"])

            await ws.send_json({"type": "response", "content": response, "session_id": SESSION_ID})
    except WebSocketDisconnect:
        pass
