"""Verify request bearer tokens with Supabase Auth."""

from typing import Annotated

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.errors import AuthApiError
from supabase_auth.types import User

from app.database.supabase import create_user_client

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> User:
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client = create_user_client(credentials.credentials)
    try:
        response = await client.auth.get_user(credentials.credentials)
    except AuthApiError as exc:
        if exc.status not in (400, 401, 403):
            raise
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    finally:
        await client.auth.close()

    if response is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response.user
