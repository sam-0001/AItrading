# Phase 9 - VPS Deployment and Reliability

## Goal
Run the system continuously on a VPS without manual startup.

## Suggested components
- Ubuntu
- Docker
- Python
- FastAPI
- PostgreSQL
- Redis
- Worker/scheduler
- Monitoring
- Alerting
- Backup system

## Requirements
- Automatic process restart for crashes
- No automatic resurrection from DEAD
- Persistent database
- Persistent state
- Health checks
- Disk-space monitoring
- CPU/RAM monitoring
- Time synchronization
- Secure secrets
- Database backups
- Structured logs

## Scheduler
The scheduler should run:
- Market-state checks
- Intraday jobs
- End-of-day processing
- Research jobs
- Daily report

## Failure behavior
If data, clock, broker-like feed, or database integrity is uncertain:
- Stop trading safely.
- Log the failure.
- Alert the owner.
- Do not invent missing data.
