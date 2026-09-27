from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from supabase_auth.errors import AuthApiError
from supabase_auth.types import User, UserResponse

from app.auth.dependencies import get_current_user

app = FastAPI()


@app.get("/private")
async def private(user: Annotated[User, Depends(get_current_user)]) -> dict[str, str]:
    return {"user_id": user.id}


def test_valid_bearer_token_returns_verified_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_tokens: list[str] = []
    closed: list[bool] = []
    user = User(
        id="b8f75ed4-14f4-412b-b042-a46208fbb21e",
        app_metadata={},
        user_metadata={},
        aud="authenticated",
        email="analyst@example.com",
        created_at=datetime.now(UTC),
    )

    async def get_user(token: str) -> UserResponse:
        seen_tokens.append(token)
        return UserResponse(user=user)

    async def close() -> None:
        closed.append(True)

    monkeypatch.setattr(
        "app.auth.dependencies.create_user_client",
        lambda token: SimpleNamespace(
            auth=SimpleNamespace(get_user=get_user, close=close)
        ),
    )

    response = TestClient(app).get(
        "/private", headers={"Authorization": "Bearer valid-jwt"}
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": user.id}
    assert seen_tokens == ["valid-jwt"]
    assert closed == [True]


@pytest.mark.parametrize("authorization", [None, "Basic abc", "Bearer"])
def test_missing_or_malformed_token_returns_401(authorization: str | None) -> None:
    headers = {"Authorization": authorization} if authorization else {}

    response = TestClient(app).get("/private", headers=headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_rejected_token_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    async def get_user(token: str) -> UserResponse:
        raise AuthApiError("Token expired", status=401, code=None)

    async def close() -> None:
        pass

    monkeypatch.setattr(
        "app.auth.dependencies.create_user_client",
        lambda token: SimpleNamespace(
            auth=SimpleNamespace(get_user=get_user, close=close)
        ),
    )

    response = TestClient(app).get(
        "/private", headers={"Authorization": "Bearer expired-jwt"}
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
