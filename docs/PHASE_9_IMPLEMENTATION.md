# Phase 9 — VPS Deployment and Reliability

## Implemented

Prepared the system for continuous unattended execution on a remote Virtual Private Server (VPS).

Key features implemented:
- **`LabScheduler`**: Automated continuous loop in `trading_lab.scheduler` that orchestrates system state transitions (`MARKET_OPEN`, `MARKET_CLOSED`, etc.), triggers EOD reports, and launches the AI research loop without manual intervention.
- **Fail-safe Halt**: Ensures that if the system is flagged as `DEAD` or encounters critical errors, the scheduler halts trading and falls back to `ERROR_SAFE` safely without attempting resurrection.
- **Containerization**: Included a `Dockerfile` and `docker-compose.yml` to scaffold PostgreSQL readiness and process restart reliability.

## Limitations
- PostgreSQL migrations using Alembic are stubbed in the configuration, but SQLite remains the default engine for safety testing until the boss provides a production Postgres DSN.
- Real scheduling sleep calls are circumvented in test mode.

## Verification

`tests/test_phase9_scheduler.py` tests that `LabScheduler` correctly follows market clock ticks and triggers end-of-day actions sequentially.

Run tests:
```sh
.venv/bin/python -m pytest
```
