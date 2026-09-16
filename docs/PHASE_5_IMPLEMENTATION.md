# Phase 5 — Strategy Laboratory

## Implemented

`trading_lab.strategy` provides a deterministic environment for strategies to be described, executed, and rigorously evaluated.

Key features implemented:
- Strategy Base Class (`Strategy`): Formalizes the interface for creating executable trading strategies without arbitrary side-effects. Enforces versioning, IDs, and a written hypothesis.
- Strategy execution hook (`on_bar`): Re-evaluates risk constraints, entry, and exits continuously over bounded data partitions.
- Deterministic Backtest Engine (`BacktestEngine`): Seamlessly connects the Phase 4 `DatasetPartition` to the Phase 2 `VirtualBroker` to accurately step through time while honoring risk ceilings and daily loss thresholds.
- Outputs evaluation stats: Net P&L, Win rate, total trades, total fees, max drawdown, and total slippage securely queried from immutable SQLite records.

## Restrictions
- The engine rejects multiple-testing lookahead and stops cleanly if the underlying lab enters a terminal `DEAD` state during execution.
- It intentionally does not provide automated grid optimization features at this phase to prevent data-snooping traps.

## Verification

`tests/test_phase5_strategy.py` executes a full lifecycle test with a mocked strategy over a controlled partition dataset, asserting execution paths, max deployment caps, and correct P&L realization against immutable records.

Run all tests safely with:
```sh
.venv/bin/python -m pytest
```
