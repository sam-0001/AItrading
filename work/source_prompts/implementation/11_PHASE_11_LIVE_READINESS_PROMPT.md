# Phase 11 Prompt - Real-Money Readiness Gate

Implement Phase 11 as a readiness and safety audit. Do not enable real-money trading automatically.

## Goal

Determine whether the system is technically ready for a separately reviewed live environment.

## Audit

Verify:
- simulator accounting;
- paper execution;
- market calendar;
- order reconciliation;
- duplicate-order prevention;
- network failure handling;
- broker rejection handling;
- restart behavior;
- state persistence;
- risk engine;
- kill switch;
- daily loss controls;
- DEAD state;
- logging;
- backups;
- credential isolation.

## Research requirements

Verify that:
- results are reproducible;
- costs/slippage are realistic;
- out-of-sample testing exists;
- walk-forward testing exists;
- experiment history is complete;
- failed experiments are retained.

## Live separation

Live credentials and live configuration must be separate from development and paper environments.

Default configuration must remain non-live.

## Human approval

Produce a readiness checklist requiring explicit human approval before any live mode is enabled.

## Do not

Do not turn on real-money execution simply because tests pass.

Do not claim profitability or safety from simulation alone.
