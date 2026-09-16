# Phase 7 — Dynamic Capital and Risk

## Implemented

`trading_lab.capital.DynamicCapitalManager` implements strict, performance-based capital allocation scaling. It evaluates the lab's virtual wallet and historical simulator trades to dynamically update the Phase 1 maximum deployment ceiling.

Key features implemented:
- **Tier-based Scaling**: Established distinct `RiskTier` levels (Tiers 1 through 4) controlling `max_deployment`.
- **Automatic Demotion**: If wallet balance falls beneath a tier boundary, `max_deployment` is instantly and automatically reduced.
- **Gated Promotion**: Wallet appreciation alone cannot trigger a tier promotion. The system demands a minimum trade count and minimum historical win rate computed directly from the immutable `simulator_trades` ledger.
- **Audit Compliance**: `MAX_DEPLOYMENT_UPDATED` events are permanently appended whenever the manager changes the Lab's risk parameters.

## Limitations
- Only tests against total system P&L rather than per-strategy isolated P&L.
- The default tiers are for simulation tuning only and must be adjusted before any theoretical live usage.

## Verification

`tests/test_phase7_capital.py` tests automatic demotion, blocked promotions (due to insufficient trades/win rates), and successful promotions, as well as invariant checks in `LabService.update_max_deployment`.

Run tests:
```sh
.venv/bin/python -m pytest
```
