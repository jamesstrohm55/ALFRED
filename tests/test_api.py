"""Tests for the A.L.F.R.E.D FastAPI endpoints."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.auth import check_rate_limit
from api.server import app

# Override auth dependency for all tests — returns a fake user
_test_user = {"id": "test-user-id", "label": "test", "rate_limit": 30}
app.dependency_overrides[check_rate_limit] = lambda: _test_user

client = TestClient(app)


# ── Chat ──────────────────────────────────────────────────────────────────────


@patch("api.server.get_response", return_value="Hello, sir.")
def test_chat_success(mock_resp):
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"] == "Hello, sir."
    assert "session_id" in data
    mock_resp.assert_called_once()


def test_chat_empty_message():
    resp = client.post("/chat", json={"message": ""})
    assert resp.status_code == 422


@patch("api.server.get_response", return_value="Hi there.")
def test_chat_with_session_id(mock_resp):
    resp = client.post("/chat", json={"message": "hello", "session_id": "my-session-123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "my-session-123"


@patch("api.server.get_response", return_value="Hi.")
def test_chat_generates_session_id(mock_resp):
    resp = client.post("/chat", json={"message": "hello"})
    data = resp.json()
    assert len(data["session_id"]) == 36  # UUID format


@patch(
    "api.server.get_conversation_history",
    return_value=[
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ],
)
def test_chat_history(mock_hist):
    resp = client.get("/chat/history?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    mock_hist.assert_called_once_with(limit=5, session_id=None, user_id="test-user-id")


@patch("api.server.get_conversation_history", return_value=[])
def test_chat_history_with_session_id(mock_hist):
    resp = client.get("/chat/history?session_id=abc-123")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "abc-123"
    mock_hist.assert_called_once_with(limit=10, session_id="abc-123", user_id="test-user-id")


@patch("api.server.get_conversation_history", return_value=[])
def test_chat_history_is_scoped_to_authenticated_user(mock_hist):
    app.dependency_overrides[check_rate_limit] = lambda: {"id": "user-2", "label": "test", "rate_limit": 30}
    try:
        resp = client.get("/chat/history?session_id=shared-session")
        assert resp.status_code == 200
        mock_hist.assert_called_once_with(limit=10, session_id="shared-session", user_id="user-2")
    finally:
        app.dependency_overrides[check_rate_limit] = lambda: _test_user


# ── Memory ────────────────────────────────────────────────────────────────────


@patch("api.server.remember", return_value=True)
def test_create_memory(mock_remember):
    resp = client.post("/memories", json={"key": "name", "value": "Alfred"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["key"] == "name"
    mock_remember.assert_called_once_with(key="name", value="Alfred", category="general", tags=None)


@patch("api.server.recall", return_value="Alfred")
def test_recall_memory_found(mock_recall):
    resp = client.get("/memories/name")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert data["value"] == "Alfred"


@patch("api.server.recall", return_value=None)
def test_recall_memory_not_found(mock_recall):
    resp = client.get("/memories/unknown")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is False
    assert data["value"] is None


@patch("api.server.forget", return_value=True)
def test_delete_memory_success(mock_forget):
    resp = client.delete("/memories/name")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@patch("api.server.forget", return_value=False)
def test_delete_memory_not_found(mock_forget):
    resp = client.delete("/memories/unknown")
    assert resp.status_code == 200
    assert resp.json()["success"] is False


@patch("api.server.list_memory", return_value={"name": "Alfred", "role": "assistant"})
def test_list_memories(mock_list):
    resp = client.get("/memories")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2
    assert data["category"] is None


@patch("api.server.list_memory", return_value={"name": "Alfred"})
def test_list_memories_with_category(mock_list):
    resp = client.get("/memories?category=personal")
    assert resp.status_code == 200
    mock_list.assert_called_once_with(category="personal")


@patch(
    "api.server.semantic_search_memory",
    return_value=[
        {"document": "name is Alfred", "similarity": 0.9, "key": "name", "category": "general"},
    ],
)
def test_search_memories(mock_search):
    resp = client.post("/memories/search", json={"query": "what is my name"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["results"][0]["key"] == "name"


@patch("api.server.semantic_search_memory", return_value=None)
def test_search_memories_empty(mock_search):
    resp = client.post("/memories/search", json={"query": "nothing"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 0


# ── Health (no auth required) ────────────────────────────────────────────────


@patch("api.server.check_connection", return_value=True)
def test_health_healthy(mock_conn):
    resp = client.get("/system/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["supabase"] is True


@patch("api.server.check_connection", return_value=False)
def test_health_degraded(mock_conn):
    resp = client.get("/system/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["supabase"] is False


# ── Auth ─────────────────────────────────────────────────────────────────────


def test_auth_missing_key_returns_401():
    # Remove the override temporarily
    app.dependency_overrides.pop(check_rate_limit, None)
    try:
        resp = client.post("/chat", json={"message": "hello"})
        assert resp.status_code == 401
        assert "Missing" in resp.json()["detail"]
    finally:
        app.dependency_overrides[check_rate_limit] = lambda: _test_user


def test_auth_invalid_key_returns_401():
    app.dependency_overrides.pop(check_rate_limit, None)
    try:
        resp = client.post("/chat", json={"message": "hello"}, headers={"x-api-key": "bad-key"})
        assert resp.status_code == 401
    finally:
        app.dependency_overrides[check_rate_limit] = lambda: _test_user
