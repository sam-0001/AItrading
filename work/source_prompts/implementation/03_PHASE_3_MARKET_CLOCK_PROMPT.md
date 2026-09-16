# Phase 3 Prompt - Indian Market Clock

Implement Phase 3 only.

## Goal

Create a reliable market-session service so the system knows when it should research, simulate trading, or remain idle.

## Requirements

Implement an exchange-calendar abstraction supporting:
- trading days;
- weekends;
- holidays;
- timezone-aware timestamps;
- session open;
- session close;
- market-closing state;
- pre-market where required.

Do not implement this using one simplistic hard-coded time comparison.

## Safety

If the calendar cannot confidently determine the session:
- do not trade;
- enter a safe state;
- log the problem;
- alert the operator where the alerting infrastructure exists.

## Scheduler interface

Expose a deterministic service such as:

`get_market_state(timestamp)`

It must be testable without waiting for real time.

## Tests

Test:
- normal trading day;
- weekend;
- holiday;
- before open;
- during session;
- after close;
- timezone conversion;
- application restart;
- unavailable/invalid calendar data.

## Integration

Connect market state to the existing state machine.

Do not implement AI or broker integration.

## Completion

Demonstrate that the simulator can automatically switch between market and research states based on the calendar.
