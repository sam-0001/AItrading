"""Idempotent Phase 1 SQLite schema migration runner.

SQLite is deliberately limited to local/test use. The repository keeps the
schema isolated so Phase 9 can replace this adapter with PostgreSQL migrations.
"""
from __future__ import annotations

import sqlite3


MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS system_state (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS wallet (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    balance TEXT NOT NULL,
    max_deployment TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS strategy_versions (
    strategy_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    specification_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (strategy_id, version)
);
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    specification_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS audit_events_append_only_update
BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are immutable'); END;
CREATE TRIGGER IF NOT EXISTS audit_events_append_only_delete
BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are immutable'); END;
CREATE TRIGGER IF NOT EXISTS strategy_versions_immutable_update
BEFORE UPDATE ON strategy_versions BEGIN SELECT RAISE(ABORT, 'strategy versions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS strategy_versions_immutable_delete
BEFORE DELETE ON strategy_versions BEGIN SELECT RAISE(ABORT, 'strategy versions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS experiments_immutable_update
BEFORE UPDATE ON experiments BEGIN SELECT RAISE(ABORT, 'experiments are immutable'); END;
CREATE TRIGGER IF NOT EXISTS experiments_immutable_delete
BEFORE DELETE ON experiments BEGIN SELECT RAISE(ABORT, 'experiments are immutable'); END;
CREATE TABLE IF NOT EXISTS simulator_cash (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    available_cash TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS simulator_positions (
    symbol TEXT PRIMARY KEY,
    quantity INTEGER NOT NULL,
    average_cost TEXT NOT NULL,
    entry_fees TEXT NOT NULL,
    entry_slippage TEXT NOT NULL,
    last_price TEXT NOT NULL,
    stop_loss TEXT,
    target_price TEXT,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS simulator_orders (
    order_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    requested_price TEXT NOT NULL,
    fill_price TEXT,
    fees TEXT NOT NULL,
    slippage TEXT NOT NULL,
    status TEXT NOT NULL,
    rejection_reason TEXT,
    strategy_id TEXT NOT NULL,
    strategy_version INTEGER NOT NULL,
    reason TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS simulator_trades (
    trade_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price TEXT NOT NULL,
    exit_price TEXT NOT NULL,
    pnl TEXT NOT NULL,
    fees TEXT NOT NULL,
    slippage TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    strategy_version INTEGER NOT NULL,
    entry_reason TEXT NOT NULL,
    exit_reason TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS simulator_orders_append_only_update
BEFORE UPDATE ON simulator_orders BEGIN SELECT RAISE(ABORT, 'orders are immutable'); END;
CREATE TRIGGER IF NOT EXISTS simulator_orders_append_only_delete
BEFORE DELETE ON simulator_orders BEGIN SELECT RAISE(ABORT, 'orders are immutable'); END;
CREATE TRIGGER IF NOT EXISTS simulator_trades_append_only_update
BEFORE UPDATE ON simulator_trades BEGIN SELECT RAISE(ABORT, 'trades are immutable'); END;
CREATE TRIGGER IF NOT EXISTS simulator_trades_append_only_delete
BEFORE DELETE ON simulator_trades BEGIN SELECT RAISE(ABORT, 'trades are immutable'); END;
"""


def apply_migrations(connection: sqlite3.Connection) -> None:
    connection.executescript(MIGRATION_SQL)
    connection.execute(
        "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, datetime('now'))",
        ("phase1_001",),
    )
    connection.commit()
