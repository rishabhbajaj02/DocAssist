# FastAPI backend

Run these commands from `backend/`:

```powershell
Copy-Item .env.example .env  # first setup only; fill in the required values
uv sync
uv run uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health` to check the service, or `http://127.0.0.1:8000/docs` for the API docs. Stop the server with Ctrl+C.

Run tests with `uv run pytest`. Add dependencies with `uv add <package>` and development dependencies with `uv add --dev <package>`. Keep environment settings in `app/config.py`; add local values to `.env` and document them in `.env.example`.
