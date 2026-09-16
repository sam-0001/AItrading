# Phase 8 — Daily Reporting and Email

## Implemented

`trading_lab.reporting.DailyReporter` provides robust daily research recaps and death alerts through an abstract `EmailSender` interface.

Key features implemented:
- **Abstract Email Interface**: Provides a `MockEmailSender` for headless unattended simulation. Real API execution can swap in via `EmailSender` protocol.
- **Daily Recap**: Reads directly from `simulator_trades` and `audit_events` to compile a summary of net P&L, fees, win rates, and AI research notes.
- **Death Report**: Triggers an immediate "ALERT: Lab Dead" summary if the wallet drops to terminal logic levels. Traces back the final trades to report on what caused the wipeout.

## Restrictions
- Reports read strictly from local SQLite state; they cannot alter lab functionality.
- A simulated backend is intentionally active to avoid accidental mail triggers during Phase 8 testing. Ensure an SMTP client is loaded into `.env` (via boss) for live phases.

## Verification

`tests/test_phase8_reporting.py` runs assertions on formatting and triggers of both standard Daily Reports and fatal Death Reports over dummy simulated datasets.

Run tests:
```sh
.venv/bin/python -m pytest
```
