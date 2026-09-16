# Architecture Assessment

## Existing repository

The supplied workspace was empty of application code, dependency manifests,
tests, configuration, database definitions, deployment files, and frontend.
There is therefore no existing implementation to reuse and no conflict with an
existing technology stack.

## Phase 1 architecture

`trading_lab` is a Python 3.12+ package. Its frozen domain values express money
and system state; `LabService` is the sole mutation authority; `SqliteStore`
is the Phase 1 durable persistence boundary. SQLite supports a self-contained,
reproducible local foundation and test suite without a network service.

The schema establishes the future persistence seams: system state, wallet,
append-only audit events, immutable strategy versions, and immutable
experiments. Database triggers prohibit update/delete for immutable records.
The service automatically persists terminal `DEAD` when the deterministic
accounting entry path reaches zero or below.

## Production database and deployment requirements

SQLite is **not** the production database decision. Before Phase 9, add a
PostgreSQL adapter plus versioned Alembic migrations, backup/restore procedure,
encrypted secrets management, container/service definitions, health checks,
and monitoring. The domain/service boundary keeps that future replacement
localized. No network service or VPS process is needed in Phase 1.

## Security assessment

No AI, shell bridge, SQL endpoint, broker adapter, or credential handling is
present. AI must remain outside `LabService` and submit validated proposals in
Phase 6; it must never receive a database connection or mutation capability.
Database append-only triggers protect historical records from ordinary update
and delete operations. Production access control and cryptographic audit
protection remain Phase 9 hardening work.

## Requirements conflicts and decisions

- The documents ask for PostgreSQL and migrations, but no existing service or
  dependency stack was supplied. Phase 1 uses standard-library SQLite for
  durable local/testing storage and documents PostgreSQL/Alembic as mandatory
  before VPS deployment. This is a safe, non-production interpretation.
- The tracker lists Phase 14 while the older master plan ends at Phase 12.
  The implementation-oriented package and pasted request add dashboard and
  acceptance phases; the tracker retains all 0–14 phases.
- A death report is mandated at death, yet reporting belongs to Phase 8.
  Phase 1 records an immutable `EXPERIMENT_DEAD` event; a rendered report is
  intentionally deferred to Phase 8 rather than prematurely implementing it.

## Dependencies and phase ordering

Phase 2 consumes `LabService` for accounting and terminal enforcement. Phase
3 adds state inputs; Phase 4–5 add reproducible data/backtests; Phase 6 adds
untrusted AI proposals; Phase 7 adds deterministic tiers; Phase 8 renders the
death event; Phase 9 replaces local infrastructure with production services.
