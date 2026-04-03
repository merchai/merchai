"""
src/storage.py — SQLite persistence for pipeline runs.

DB path defaults to data/merchai.db, overridable via DB_PATH env variable.

Schema
------
runs(id INTEGER PK, prompt TEXT, timestamp TEXT, raw_response TEXT, brands_json TEXT)
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "merchai.db"


def _db_path() -> Path:
    env = os.getenv("DB_PATH")
    return Path(env) if env else _DEFAULT_DB_PATH


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the runs table if it doesn't exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt        TEXT    NOT NULL,
                timestamp     TEXT    NOT NULL,
                raw_response  TEXT    NOT NULL,
                brands_json   TEXT    NOT NULL
            )
            """
        )


def save_run(prompt: str, response: str, brands: list[str]) -> int:
    """Persist a pipeline run. Returns the new row id."""
    timestamp = datetime.now(timezone.utc).isoformat()
    brands_json = json.dumps(brands)
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO runs (prompt, timestamp, raw_response, brands_json) VALUES (?, ?, ?, ?)",
            (prompt, timestamp, response, brands_json),
        )
        return cursor.lastrowid  # type: ignore[return-value]


def get_all_runs() -> list[dict]:
    """Return all runs ordered by most recent first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, prompt, timestamp, raw_response, brands_json FROM runs ORDER BY id DESC"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "prompt": row["prompt"],
            "timestamp": row["timestamp"],
            "raw_response": row["raw_response"],
            "brands": json.loads(row["brands_json"]),
        }
        for row in rows
    ]
