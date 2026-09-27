# Phase 3 Chat Shell Implementation Plan

**Goal:** Deliver a working authenticated chat shell with persisted threads and a streamed stub reply.

**Architecture:** FastAPI owns thread access, message storage, and the AI SDK data stream. The React SPA lists threads, loads history, and sends messages with the Supabase bearer token. Supabase service-role writes are explicitly constrained by the verified user and thread ownership.

**Tech Stack:** FastAPI, Supabase Postgres, React Router, TypeScript, AI SDK React.

**Spec:** `docs/todos.md` Phase 3 and `docs/architecture.md` streaming contract.

## Backend

1. Add `app/database/chats.py` with user-scoped list/create/load helpers and atomic turn persistence. Resolve ownership before every thread read or write; return 403 for another user's thread and 404 for unknown threads.
2. Add `app/api/chat.py` with `GET /chat/threads`, `POST /chat/threads`, `GET /chat/threads/{id}`, and `POST /chat/stream`. Validate the last AI SDK user message, stream text parts, then save both messages after successful completion.
3. Register the router and add unit tests for auth, ownership, stream payload, and persistence behavior.

## Frontend

4. Install the AI SDK React client and add a chat transport that supplies the current Supabase access token.
5. Replace the signed-in placeholder with `/chat` and `/chat/:threadId` routes. Show a sidebar, history, message list, composer, and streaming state. Refresh thread history after a successful turn.
6. Run backend unit tests, TypeScript build, lint, and manually verify with credentials when available.

## Constraints

- Keep existing Phase 2 uncommitted work intact.
- Use `app.config.settings` and `src/lib/env.ts` for environment settings.
- No frontend test suite; verify with typecheck and lint.
- Persist only completed turns.
