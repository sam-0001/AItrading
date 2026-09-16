# Phase 1 - Foundation and Rules

## Goal
Create the project skeleton and formalize the system's rules before implementing AI or broker integration.

## Build
- Repository structure
- Configuration management
- Environment handling
- PostgreSQL schema/migrations
- Structured logging
- Strategy/version identifiers
- Experiment identifiers
- System state machine
- `SYSTEM_RULES.md`
- Automated tests

## Required system states
- `INITIALIZING`
- `PRE_MARKET`
- `MARKET_OPEN`
- `MARKET_CLOSING`
- `MARKET_CLOSED`
- `RESEARCH`
- `DEAD`
- `ERROR_SAFE`

`DEAD` must be terminal for the experiment.

## Hard wallet rule
Starting virtual wallet: ₹1,000.

Initial maximum deployment: ₹500.

The wallet is an accounting object, not real money.

If total wallet balance <= ₹0:
1. Persist `DEAD`.
2. Stop new simulated trades.
3. Cancel simulated pending orders.
4. Stop strategy execution.
5. Prevent automatic restart into a trading state.
6. Preserve all data.
7. Generate a death report.

## Tests
- State transitions are valid.
- Invalid transitions are rejected.
- DEAD survives process restart.
- DEAD cannot be changed by strategy/AI code.
- Wallet starts at exactly ₹1,000.
- Initial maximum deployment is ₹500.
- Historical records are immutable.
