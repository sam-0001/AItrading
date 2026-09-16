# Requirements Map

The map reconciles the pasted master request with the two supplied document
packages. “Deferred” means deliberately not implemented before its phase.

| Requirement | Source | Phase | Implementation location | Dependency | Acceptance test |
| --- | --- | ---: | --- | --- | --- |
| Python core, modular separation | Pasted §1; both master plans | 1 | `trading_lab/` | Python 3.12+ | package imports and tests run |
| ₹1,000 virtual wallet | Pasted §§5–7; Phase 1 docs | 1 | `domain.py`, `services.py` | durable store | initial balance exact |
| ₹500 initial deployment ceiling | Pasted §7; Phase 1 docs | 1 | `domain.py`, `services.py` | durable store | ceiling exact |
| Valid state machine | Phase 1 docs | 1 | `services.py` | durable state | invalid transition rejected |
| Terminal durable DEAD | Pasted §§10,34; Phase 1 docs | 1 | `services.py`, `store.py` | accounting path | zero→DEAD→restart stays DEAD |
| Accounting-only wallet mutation | Pasted §§6,28; Phase 1 prompt | 1 | `LabService.record_accounting_entry` | state service | direct boundary is absent; audited entry succeeds |
| Append-only history | Pasted §§15,22; Phase 1 docs | 1 | `migrations.py`, `store.py` | database | update rejected by trigger |
| Configuration and structured logging | Phase 1 docs | 1 | `config.py`, `logging.py` | environment | initialization smoke test |
| PostgreSQL/Alembic production store | Pasted §1; Phase 1 plan | Deferred to 9 | architecture assessment | production deployment decision | migration/deployment validation |
| Execution simulator, fees, slippage | Phase 2 docs | 2 | `simulator.py`, simulator schema | foundation | profitable/loss, costs, ledger tests |
| Market orders, positions, cash, realized/unrealized P&L | Phase 2 docs | 2 | `simulator.py` | wallet accounting | position, cash, P&L fixtures |
| Deployment and daily-loss controls | Phase 2 docs | 2 | `simulator.py` | wallet/risk configuration | over-limit and daily-loss rejection tests |
| Stop-loss and target exits | Phase 2 docs | 2 | `VirtualBroker.process_price` | deterministic price input | stop/target tests |
| Immutable execution/trade records | Phase 2 docs | 2 | `migrations.py` | database | append-only ledger schema |
| Indian session/calendar | Phase 3 docs | 3 | `clock.py` | state machine | calendar boundary tests |
| Versioned data/no leakage | Phase 4 docs | 4 | `data.py` | storage seam | partition tests |
| Backtesting and strategy lab | Phase 5 docs | 5 | `strategy.py` | data pipeline | reproducibility tests |
| Untrusted AI proposal boundary | Pasted §§12,28; Phase 6 docs | 6 | `ai_research.py` | strategy/backtester | malicious mock rejected |
| Capital tiers | Phase 7 docs | 7 | `capital.py` | simulator data | promotion/demotion tests |
| Daily/death email reports | Phase 8 docs | 8 | `reporting.py` | trades/experiments | mock mail tests |
| VPS reliability | Phase 9 docs | 9 | `scheduler.py`, `docker-compose.yml` | PostgreSQL, scheduler | restart and health tests |
| Angel One paper adapter; live disabled | Phase 10 docs | 10 | `broker_adapter.py` | official current verification | paper intercept tests |
| Live readiness gate | Phase 11 docs | 11 | `readiness.py` | all prior phases | checklist audit |
| Paper pipeline/human review | Phase 12 docs | 12 | `publication.py` | validated results | traceability tests |
| Read-only dashboard | Phase 13 docs | 13 | `dashboard.py` | APIs | no bypass controls |
| Full acceptance | Acceptance prompt | 14 | `test_phase14_acceptance.py` | phases 1–13 | end-to-end scenarios |
