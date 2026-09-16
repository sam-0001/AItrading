# Phase 2 — Virtual Simulator

## Implemented

`trading_lab.simulator.VirtualBroker` deterministically simulates market buy
and sell orders. It stores append-only orders and completed trades, maintains
available virtual cash and positions, calculates a configurable brokerage rate
and adverse slippage, and records realized and unrealized P&L.

The simulator enforces the Phase 1 maximum deployment ceiling, available cash,
position availability, duplicate-order rejection, and a configurable daily
realized-loss entry block. Stop-loss and target values are evaluated only when
the caller supplies a deterministic price through `process_price`; there is no
live data feed.

Every change in total wallet equity uses `LabService.record_accounting_entry`.
If the resulting virtual equity is zero or below, the Phase 1 terminal `DEAD`
rule applies immediately and survives a new process/store instance.

## Explicit limitations

- This is a paper simulator, not evidence of live performance.
- It accepts only supplied market prices. There is no live feed, calendar, or
  scheduler; those belong to Phases 3, 4, and 9.
- Limit-order handling is deferred until Phase 4 provides deterministic bar or
  quote data from which a fill can be validated. No invented fills are used.
- Charges are a configurable generic brokerage rate and slippage bps; Indian
  exchange-specific charge schedules require a documented data/configuration
  source before being introduced.
- No AI, broker endpoint, real-money path, or autonomous strategy generation
  exists.

## Verification

`tests/test_phase2_simulator.py` covers profitable and losing trades,
insufficient cash, maximum deployment, stop loss, target exits, fees, slippage,
duplicate orders, daily loss limit, terminal death, restart after death, and
historical trade persistence. Run all safety tests with:

```sh
.venv/bin/python -m pytest
```
