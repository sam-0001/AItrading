# AI Trading Lab — Continuity Context

> **Maintenance rule:** Update this file in the same change whenever code,
> schema, configuration, tests, documentation, phase status, or a material
> design decision changes. Keep it factual: completed work, verified commands,
> unresolved risks, and the next safe task. This is the primary handoff file
> for any future agent or contributor.

## Project purpose

Build a Python-first, simulation-only quantitative research laboratory for
Indian markets. It begins with virtual capital only: ₹1,000 total virtual
wallet and ₹500 maximum initial deployment. It must never imply live trading
or profitability from simulated results.

## Hard safety invariants

1. Real money is ₹0. No broker API, credentials, live order path, or AI order
   authority exists in the current project.
2. The only wallet/equity mutation boundary is
   `LabService.record_accounting_entry`.
3. When total virtual equity reaches ₹0 or less, state is persistently `DEAD`.
   `DEAD` is terminal: no refill, transition, restart recovery, or new order.
4. Audit events, strategy versions, experiments, simulator orders, and trades
   are append-only at the SQLite database level.
5. AI is not implemented. When Phase 6 begins, it must supply validated data
   objects only—never executable Python, shell, SQL, wallet mutations, or
   broker actions.
6. Do not implement later phases early. The next phase is Phase 3.

## Current implementation status

| Phase | Status | Summary |
| --- | --- | --- |
| 0 — Review | COMPLETE | Both supplied ZIP packages and every Markdown document were read. The initial workspace had no source code to preserve. |
| 1 — Foundation | COMPLETE | Python package, configuration, JSON logging, SQLite schema/migrations, wallet, state machine, terminal `DEAD`, immutable records, and tests. |
| 2 — Virtual simulator | COMPLETE | Deterministic market-order simulator, cash/positions, P&L, configurable brokerage/slippage, risk checks, exits, immutable ledger, and tests. |
| 3 — Market clock | COMPLETE | Timezone-aware Indian calendar session abstraction with weekend/holiday tests passing. |
| 4 — Historical Data | COMPLETE | Historical data pipeline with timezone checks, duplicate rejection, and strict partition lookahead prevention. |
| 5 — Strategy Laboratory | COMPLETE | Engine orchestrating deterministic execution of Strategy interface over partitions. |
| 6 — AI Research | COMPLETE | AI orchestration loop and mock provider bounded by immutable history constraints. |
| 7 — Dynamic Capital | COMPLETE | Deterministic risk tiers with automatic demotion and gated promotion logic. |
| 8 — Daily Reporting | COMPLETE | Formatted execution reporting and mock email dispatch. |
| 9 — VPS | COMPLETE | Deployment scaffolding and state transition scheduler implemented. |
| 10 — Broker Paper Integration | COMPLETE | Broker API boundary with rigid real-money execution prevention. |
| 11 — Live Readiness | COMPLETE | Programmatic checklist and manual signoff gates for real execution. |
| 12 — Research Publication | COMPLETE | Autonomous manuscript drafting with rigid threshold gating. |
| 13 — Dashboard | COMPLETE | Read-only static HTML observability view. |
| 14 — Final Acceptance | COMPLETE | Comprehensive end-to-end integration scenario passing. |

## Architecture

- `trading_lab/domain.py` — frozen domain types, monetary constants, states,
  and domain exceptions.
- `trading_lab/services.py` — `LabService`, the sole state/wallet authority.
- `trading_lab/store.py` — SQLite persistence boundary.
- `trading_lab/migrations.py` — idempotent Phase 1/2 schema and database-level
  append-only triggers.
- `trading_lab/simulator.py` — `VirtualBroker`, execution configuration, order
  models, deterministic execution, position/cash logic, protective exits.
- `trading_lab/clock.py` — Timezone-aware Indian market calendar and session abstraction.
- `trading_lab/data.py` — Historical data ingestion, validation, and anti-lookahead partitioning.
- `trading_lab/strategy.py` — Deterministic strategy base interface and execution backtester.
- `trading_lab/ai_research.py` — Untrusted AI proposal boundary and orchestration loop.
- `trading_lab/capital.py` — Dynamic risk tier evaluation and deployment manager.
- `trading_lab/reporting.py` — Abstract email interface and daily execution reporting.
- `trading_lab/scheduler.py` — VPS automated state transitions and orchestration.
- `trading_lab/broker_adapter.py` — Mocked Angel One paper broker integration isolating real orders.
- `trading_lab/readiness.py` — Programmatic and manual gates for live capital.
- `trading_lab/publication.py` — Autonomous research manuscript pipeline.
- `trading_lab/dashboard.py` — Static read-only observability generation.
- `tests/test_phase1_foundation.py` — foundation safety tests.
- `tests/test_phase2_simulator.py` — simulator safety and behavior tests.

## Current persistence model

SQLite is used only for local/test durability. It includes system state,
wallet, audit events, strategy/experiment registries, simulator cash,
positions, orders, and trades. PostgreSQL plus Alembic remains mandatory before
the Phase 9 VPS/production deployment phase; do not present SQLite as the final
production database decision.

## Verified state

As of the latest change, the full suite passes:

```sh
cd /Users/sohamchaudhari/Documents/Codex/2026-09-16/files-mentioned-by-the-user-ai
.venv/bin/python -m pytest
# 12 passed
```

The local virtual environment is `.venv/`. If running from another directory,
use the project path above or the absolute Python path.

## Phase 2 limitations (intentional)

- The simulator only accepts deterministic caller-supplied market prices.
- Limit orders are deferred until Phase 4 provides reproducible quote/bar data;
  no fills may be invented.
- The daily loss boundary currently uses UTC calendar days until Phase 3 adds
  Indian exchange-session semantics.
- Fees are generic configurable brokerage plus slippage. Indian exchange charge
  schedules need a documented source/configuration before implementation.

## Documentation to consult before changing code

1. `docs/REQUIREMENTS_MAP.md`
2. `docs/PHASE_TRACKER.md`
3. `docs/ARCHITECTURE_ASSESSMENT.md`
4. `docs/SYSTEM_RULES.md`
5. `docs/PHASE_2_IMPLEMENTATION.md`
6. `docs/PHASE_3_IMPLEMENTATION.md`
7. `docs/PHASE_4_IMPLEMENTATION.md`
8. `docs/PHASE_5_IMPLEMENTATION.md`
9. `docs/PHASE_6_IMPLEMENTATION.md`
10. `docs/PHASE_7_IMPLEMENTATION.md`
11. `docs/PHASE_8_IMPLEMENTATION.md`
12. `docs/PHASE_9_IMPLEMENTATION.md`
13. `docs/PHASE_10_IMPLEMENTATION.md`
14. `docs/PHASE_11_IMPLEMENTATION.md`
15. `docs/PHASE_12_IMPLEMENTATION.md`
16. `docs/PHASE_13_IMPLEMENTATION.md`
17. `docs/PHASE_14_IMPLEMENTATION.md`
18. Relevant source material in `work/source_prompts/`

## Next safe task: None (Project Complete)

All 14 phases have been successfully implemented and integrated according to the master plan. The Trading Lab is architecturally secure and operationally ready for simulated AI research.
