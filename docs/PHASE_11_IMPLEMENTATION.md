# Phase 11 — Real-Money Readiness

## Implemented

`trading_lab.readiness` introduces the final programmatic and operational gate designed to block the system from ever touching live capital without explicit sign-offs and audited condition checks.

Key features implemented:
- **`LiveReadinessGate`**: Evaluates a rigid checklist of system prerequisites (e.g., minimum paper trades executed, DEAD state validation observed, SEBI compliance checks).
- **Hard Error Blocking**: Triggers a `ReadinessError` if *any* checklist item is incomplete, completely aborting live-mode initialization.
- **Manual Audit Overrides**: Provides a `manual_override_signoff` method that allows authorized humans to certify manual checks (like broker statement reconciliations) while leaving a durable `READINESS_SIGNOFF` audit trace in the database.

## Limitations
- Certain validations (SEBI rules, manual accounting matches) will always require a human operator to invoke the override. They cannot be fully automated by design.

## Verification

`tests/test_phase11_readiness.py` confirms that the Live Readiness Gate blocks live initialization by default and verifies that manual bypasses correctly log unalterable audit trails.

Run tests:
```sh
.venv/bin/python -m pytest
```
