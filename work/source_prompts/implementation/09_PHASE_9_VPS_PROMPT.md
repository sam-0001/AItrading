# Phase 9 Prompt - VPS Deployment

Implement Phase 9 only.

## Goal

Deploy the system as a reliable 24/7 service on a VPS.

## Suggested stack

Use the existing project's technologies where sensible.

Potential components:
- Ubuntu;
- Docker;
- Python;
- PostgreSQL;
- Redis;
- worker/scheduler;
- API/dashboard;
- monitoring.

Do not rewrite the application just to use these technologies.

## Requirements

Implement:
- persistent services;
- health checks;
- automatic recovery from ordinary process crashes;
- persistent database;
- persistent system state;
- backups;
- structured logs;
- resource monitoring;
- time synchronization checks;
- secure secret handling.

## Critical DEAD behavior

A VPS restart must NEVER resurrect a DEAD experiment.

Startup sequence must load persisted state before enabling trading.

## Failure behavior

If:
- database is unavailable;
- market clock is uncertain;
- data integrity fails;
- required service is unavailable;

the system must fail closed and not simulate trades using invented information.

## Scheduler

Schedule:
- market state checks;
- intraday processing;
- end-of-day processing;
- research jobs;
- daily report.

## Deployment

Provide:
- Docker configuration where appropriate;
- environment template;
- deployment instructions;
- health-check instructions;
- rollback instructions.

## Tests

Test restart during each important state, especially DEAD.
