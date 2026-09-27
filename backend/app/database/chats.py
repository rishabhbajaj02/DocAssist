"""User-scoped chat persistence."""

from uuid import UUID

from fastapi import HTTPException

from app.database.supabase import create_service_role_client


async def list_threads(user_id: str) -> list[dict]:
    client = create_service_role_client()
    response = await (
        client.table("chat_threads")
        .select("id,title,created_at,updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return response.data


async def create_thread(user_id: str, email: str) -> dict:
    client = create_service_role_client()
    await client.table("users").upsert({"id": user_id, "email": email}).execute()
    response = await client.table("chat_threads").insert(
        {"user_id": user_id, "title": "New chat"}
    ).execute()
    return response.data[0]


async def require_thread(thread_id: UUID, user_id: str) -> dict:
    client = create_service_role_client()
    response = await client.table("chat_threads").select("*").eq("id", str(thread_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Thread not found")
    thread = response.data[0]
    if thread["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Thread belongs to another user")
    return thread


async def load_thread(thread_id: UUID, user_id: str) -> dict:
    thread = await require_thread(thread_id, user_id)
    client = create_service_role_client()
    response = await (
        client.table("chat_messages")
        .select("id,role,content,message_json,position,created_at")
        .eq("thread_id", str(thread_id))
        .order("position")
        .execute()
    )
    return {"thread": thread, "messages": response.data}


async def save_turn(thread_id: UUID, user_id: str, user_text: str, reply: str) -> None:
    await require_thread(thread_id, user_id)
    client = create_service_role_client()
    existing = await (
        client.table("chat_messages").select("position")
        .eq("thread_id", str(thread_id)).order("position", desc=True).limit(1).execute()
    )
    position = existing.data[0]["position"] + 1 if existing.data else 0
    await client.table("chat_messages").insert([
        {"thread_id": str(thread_id), "position": position, "role": "user", "content": user_text,
         "message_json": {"role": "user", "parts": [{"type": "text", "text": user_text}]}},
        {"thread_id": str(thread_id), "position": position + 1, "role": "assistant", "content": reply,
         "message_json": {"role": "assistant", "parts": [{"type": "text", "text": reply}]}},
    ]).execute()
    thread = await client.table("chat_threads").select("title").eq("id", str(thread_id)).execute()
    if thread.data[0]["title"] == "New chat":
        await client.table("chat_threads").update({"title": user_text[:80]}).eq("id", str(thread_id)).execute()
