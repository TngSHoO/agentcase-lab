from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from .models import CaseRecord, TraceStep
from .seed import build_demo_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "agentcase.db"


def get_db_path() -> Path:
    configured = os.getenv("AGENTCASE_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DB_PATH


def _connect() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            scenario TEXT NOT NULL,
            model_name TEXT NOT NULL,
            status TEXT NOT NULL,
            root_cause TEXT NOT NULL,
            severity TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            token_cost REAL NOT NULL,
            created_at TEXT NOT NULL,
            user_request TEXT NOT NULL,
            final_answer TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            evidence TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            after_status TEXT NOT NULL,
            after_latency_ms INTEGER NOT NULL,
            after_token_count INTEGER NOT NULL,
            after_token_cost REAL NOT NULL,
            fix_summary TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trace_steps (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            step_type TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            token_cost REAL NOT NULL,
            input_data TEXT NOT NULL,
            output_data TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        );
        """
    )


def _insert_case(connection: sqlite3.Connection, case: CaseRecord) -> None:
    payload = case.model_dump()
    columns = ", ".join(payload.keys())
    placeholders = ", ".join("?" for _ in payload)
    connection.execute(
        f"INSERT OR REPLACE INTO cases ({columns}) VALUES ({placeholders})",
        tuple(payload.values()),
    )


def _insert_step(connection: sqlite3.Connection, step: TraceStep) -> None:
    payload = step.model_dump()
    payload["input_data"] = json.dumps(payload["input_data"], ensure_ascii=False)
    payload["output_data"] = json.dumps(payload["output_data"], ensure_ascii=False)
    columns = ", ".join(payload.keys())
    placeholders = ", ".join("?" for _ in payload)
    connection.execute(
        f"INSERT OR REPLACE INTO trace_steps ({columns}) VALUES ({placeholders})",
        tuple(payload.values()),
    )


def ensure_database() -> Path:
    with _connect() as connection:
        _create_schema(connection)
        count = connection.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        if count == 0:
            cases, steps = build_demo_dataset()
            for case in cases:
                _insert_case(connection, case)
            for step in steps:
                _insert_step(connection, step)
            connection.commit()
    return get_db_path()


def reset_demo_database() -> None:
    with _connect() as connection:
        _create_schema(connection)
        connection.execute("DELETE FROM trace_steps")
        connection.execute("DELETE FROM cases")
        cases, steps = build_demo_dataset()
        for case in cases:
            _insert_case(connection, case)
        for step in steps:
            _insert_step(connection, step)
        connection.commit()


def get_cases() -> list[dict[str, Any]]:
    ensure_database()
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


def get_case(case_id: str) -> dict[str, Any] | None:
    ensure_database()
    with _connect() as connection:
        row = connection.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    return dict(row) if row else None


def get_steps(case_id: str) -> list[dict[str, Any]]:
    ensure_database()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT * FROM trace_steps WHERE case_id = ? ORDER BY sequence", (case_id,)
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["input_data"] = json.loads(item["input_data"])
        item["output_data"] = json.loads(item["output_data"])
        result.append(item)
    return result
