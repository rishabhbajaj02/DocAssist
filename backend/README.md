# FastAPI backend

Run these commands from `backend/`:

```powershell
Copy-Item .env.example .env  # first setup only; fill in the required values
uv sync
uv run uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health` to check the service, or `http://127.0.0.1:8000/docs` for the API docs. Stop the server with Ctrl+C.

Run tests with `uv run pytest`. Add dependencies with `uv add <package>` and development dependencies with `uv add --dev <package>`. Keep environment settings in `app/config.py`; add local values to `.env` and document them in `.env.example`.

For schema changes, update `app/database/models/`, generate a candidate with `uv run alembic revision --autogenerate -m "description"`, and review it before applying. The first revision is `alembic/versions/f14a75fda002_initial_schema.py`. Preview its SQL without connecting to the database with `uv run alembic upgrade head --sql`; apply it only when ready with `uv run alembic upgrade head` using the direct Supabase database URL.
