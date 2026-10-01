"""Entry point for hosts that run `uvicorn main:app` from the repository root.

The backend lives in backend/main.py; this re-exports its app.
"""

from backend.main import app  # noqa: F401
