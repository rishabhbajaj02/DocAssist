"""Chat API contract without live Supabase access."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from supabase_auth.types import User

from app.auth.dependencies import get_current_user
from app.database import chats
from app.main import app

USER_ID = "b8f75ed4-14f4-412b-b042-a46208fbb21e"
THREAD_ID = "35e58cb5-449e-49c5-8cf2-96050667ad54"


def test_stream_emits_reply_and_persists_completed_turn(monkeypatch) -> None:
    user = User(
        id=USER_ID, app_metadata={}, user_metadata={}, aud="authenticated",
        email="analyst@example.com", created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_current_user] = lambda: user
    saved: list[tuple] = []

    async def require_thread(thread_id: UUID, user_id: str) -> dict:
        assert str(thread_id) == THREAD_ID
        assert user_id == USER_ID
        return {"id": THREAD_ID, "user_id": USER_ID}

    async def save_turn(thread_id: UUID, user_id: str, question: str, reply: str) -> None:
        saved.append((thread_id, user_id, question, reply))

    monkeypatch.setattr("app.api.chat.chats.require_thread", require_thread)
    monkeypatch.setattr("app.api.chat.chats.save_turn", save_turn)

    try:
        response = TestClient(app).post("/chat/stream", json={
            "threadId": THREAD_ID,
            "messages": [{"role": "user", "parts": [{"type": "text", "text": "Revenue?"}]}],
        })
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["x-vercel-ai-ui-message-stream"] == "v1"
    assert '"type": "text-delta"' in response.text
    assert "data: [DONE]" in response.text
    assert saved[0][2] == "Revenue?"
    assert "stubbed response" in saved[0][3]


def test_other_users_thread_is_forbidden(monkeypatch) -> None:
    class Query:
        def select(self, _columns): return self
        def eq(self, _column, _value): return self
        async def execute(self):
            return type("Response", (), {"data": [{"id": THREAD_ID, "user_id": "another-user"}]})()

    monkeypatch.setattr("app.database.chats.create_service_role_client", lambda: type(
        "Client", (), {"table": lambda self, _name: Query()}
    )())

    with pytest.raises(HTTPException) as error:
        asyncio.run(chats.require_thread(UUID(THREAD_ID), USER_ID))
    assert error.value.status_code == 403
