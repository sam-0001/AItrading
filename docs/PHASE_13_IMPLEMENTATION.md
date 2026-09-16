# Phase 13 — Read-Only Dashboard

## Implemented

`trading_lab.dashboard` provides a strict, read-only HTML observability layer for the system.

Key features implemented:
- **State Hydration**: Generates a static HTML view pulling directly from the immutable `sqlite` ledger (System State, Virtual Balance, Risk Tiers).
- **Audit Visbility**: Renders recent trades and system `audit_events` for monitoring.
- **Zero-Mutation Constraint**: By design, the dashboard generates pure HTML without any `<form>`, `<button>`, or API endpoint capable of altering state or bypassing the established Phase 1/11 safety gates.

## Limitations
- Generates static HTML markup. Requires a web server (e.g., FastAPI, Nginx) configured in Phase 9 to serve this string over HTTP for real-world remote viewing.

## Verification

`tests/test_phase13_dashboard.py` confirms that the dashboard generates successfully without crashing and asserts the absence of any HTML mutation tags.

Run tests:
```sh
.venv/bin/python -m pytest
```
