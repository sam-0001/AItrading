from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from .domain import AuditEvent, ImmutableRecordError, WalletSnapshot
from .migrations import apply_migrations


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_now() -> str:
    return utc_now().isoformat()


class SqliteStore:
    """Persistence boundary. Domain services—not AI/strategy callers—own mutations."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            apply_migrations(connection)
            yield connection
            connection.commit()
        finally:
            connection.close()

    def append_event(self, event_type: str, payload: dict) -> AuditEvent:
        event = AuditEvent(str(uuid4()), event_type, utc_now(), json.dumps(payload, sort_keys=True))
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO audit_events(event_id,event_type,occurred_at,payload_json) VALUES (?,?,?,?)",
                (event.event_id, event.event_type, event.occurred_at.isoformat(), event.payload_json),
            )
        return event

    def events(self) -> list[AuditEvent]:
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM audit_events ORDER BY occurred_at, event_id").fetchall()
        return [AuditEvent(r["event_id"], r["event_type"], datetime.fromisoformat(r["occurred_at"]), r["payload_json"]) for r in rows]

    def update_event_for_test_only(self, event_id: str) -> None:
        try:
            with self.connection() as conn:
                conn.execute("UPDATE audit_events SET event_type = 'tampered' WHERE event_id = ?", (event_id,))
        except sqlite3.DatabaseError as error:
            raise ImmutableRecordError(str(error)) from error

    def create_immutable_strategy_version(self, strategy_id: str, version: int, specification: dict) -> None:
        with self.connection() as conn:
            conn.execute("INSERT INTO strategy_versions VALUES (?,?,?,?)", (strategy_id, version, json.dumps(specification, sort_keys=True), iso_now()))

    def create_immutable_experiment(self, experiment_id: str, specification: dict) -> None:
        with self.connection() as conn:
            conn.execute("INSERT INTO experiments VALUES (?,?,?)", (experiment_id, json.dumps(specification, sort_keys=True), iso_now()))

    def wallet(self) -> WalletSnapshot | None:
        with self.connection() as conn:
            row = conn.execute("SELECT balance,max_deployment,updated_at FROM wallet WHERE singleton=1").fetchone()
        if row is None:
            return None
        return WalletSnapshot(Decimal(row["balance"]), Decimal(row["max_deployment"]), datetime.fromisoformat(row["updated_at"]))
