"""Pydantic schemas for the A.L.F.R.E.D REST API."""

from __future__ import annotations

from pydantic import BaseModel, Field

# ── Chat ──────────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    response: str
    session_id: str


class ConversationMessage(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    messages: list[ConversationMessage]
    session_id: str


# ── Memory ────────────────────────────────────────────────────────────────────


class MemoryCreateRequest(BaseModel):
    key: str
    value: str
    category: str = "general"
    tags: list[str] | None = None


class MemoryCreateResponse(BaseModel):
    success: bool
    key: str
    message: str


class MemoryRecallResponse(BaseModel):
    key: str
    value: str | None
    found: bool


class MemoryListResponse(BaseModel):
    memories: dict[str, str]
    count: int
    category: str | None


class MemoryDeleteResponse(BaseModel):
    success: bool
    key: str
    message: str


class MemorySearchRequest(BaseModel):
    query: str
    n_results: int = Field(default=5, ge=1, le=20)


class MemorySearchResult(BaseModel):
    document: str
    similarity: float
    key: str
    category: str


class MemorySearchResponse(BaseModel):
    results: list[MemorySearchResult]
    query: str
    count: int


# ── System ────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str
    supabase: bool
    version: str
