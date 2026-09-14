"""
Vyapar Setu — SQLAlchemy Database Configuration
Supports SQLite (default, zero-setup) and PostgreSQL via DATABASE_URL env var.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── Resolve DATABASE_URL ──────────────────────────────────────────────────────
_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vyapar_setu.db")

# SQLite optimisations (WAL mode + foreign keys)
_CONNECT_ARGS: dict = {}
if _DATABASE_URL.startswith("sqlite"):
    _CONNECT_ARGS = {"check_same_thread": False}

engine = create_engine(
    _DATABASE_URL,
    connect_args=_CONNECT_ARGS,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

if _DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base Model ───────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ───────────────────────────────────────────────────────
def get_db():
    """Yield a DB session and close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
