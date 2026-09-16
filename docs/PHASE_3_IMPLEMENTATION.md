# Phase 3 — Market Clock

## Implemented

`trading_lab.clock.MarketClock` provides an Indian exchange calendar and session abstraction. It handles timezone conversions securely and is built strictly for the `Asia/Kolkata` time zone.

Key features implemented:
- Strict timezone verification (rejects naive datetimes and returns `ERROR_SAFE`).
- Holiday handling via an injected list of dates.
- Native weekend detection (Saturdays and Sundays).
- Accurate Indian stock market state evaluation into `SystemState`:
  - `MARKET_CLOSED` (< 09:00, or >= 15:30)
  - `PRE_MARKET` (09:00 to 09:15)
  - `MARKET_OPEN` (09:15 to 15:15)
  - `MARKET_CLOSING` (15:15 to 15:30)
- Fallback logic to safely return `SystemState.ERROR_SAFE` on uncertain calendar data or internal errors.

## Explicit Limitations

- The holidays must be explicitly provided at instantiation; no automatic API fetching of live exchange holiday calendars is performed (abiding by the local-only simulation rules of Phase 1-3).
- Does not integrate with any real live broker feed to determine unexpected market closures or trading halts.
- Uses intraday auto-square off time approximation for `MARKET_CLOSING` (15:15 to 15:30).

## Verification

`tests/test_phase3_clock.py` covers UTC timezone conversion, holiday parsing, weekend handling, naive datetime rejection, and boundary limits for standard Indian market sessions.

Run all tests safely with:
```sh
.venv/bin/python -m pytest
```
