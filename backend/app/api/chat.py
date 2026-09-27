"""Authenticated thread routes and a stub AI SDK data stream."""

import asyncio
import json
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from supabase_auth.types import User

from app.auth.dependencies import get_current_user
from app.database import chats

router = APIRouter(prefix="/chat", tags=["chat"])
CurrentUser = Annotated[User, Depends(get_current_user)]


class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class IncomingMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    parts: list[TextPart]


class StreamRequest(BaseModel):
    threadId: UUID
    messages: list[IncomingMessage] = Field(min_length=1)


def stream_part(part: dict) -> str:
    return f"data: {json.dumps(part)}\n\n"


@router.get("/threads")
async def threads(user: CurrentUser) -> list[dict]:
    return await chats.list_threads(user.id)


@router.post("/threads", status_code=201)
async def new_thread(user: CurrentUser) -> dict:
    return await chats.create_thread(user.id, user.email or "")


@router.get("/threads/{thread_id}")
async def thread(thread_id: UUID, user: CurrentUser) -> dict:
    return await chats.load_thread(thread_id, user.id)


@router.post("/stream")
async def stream(request: StreamRequest, user: CurrentUser) -> StreamingResponse:
    await chats.require_thread(request.threadId, user.id)
    last = request.messages[-1]
    if last.role != "user":
        raise HTTPException(status_code=422, detail="Last message must be from user")
    text = "".join(part.text for part in last.parts).strip()
    if not text:
        raise HTTPException(status_code=422, detail="Message text required")
    reply = "This is a stubbed response. Document retrieval is coming next."
    message_id = str(uuid4())

    async def events():
        yield stream_part({"type": "start", "messageId": message_id})
        yield stream_part({"type": "text-start", "id": "reply"})
        for word in reply.split(" "):
            yield stream_part({"type": "text-delta", "id": "reply", "delta": word + " "})
            await asyncio.sleep(0.03)
        yield stream_part({"type": "text-end", "id": "reply"})
        await chats.save_turn(request.threadId, user.id, text, reply)
        yield stream_part({"type": "finish"})
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"x-vercel-ai-ui-message-stream": "v1"})
