# Phase 11 - Real-Money Readiness

## Goal
Determine whether the system is technically and operationally ready for any real-money experiment.

## Requirements
Before enabling live execution:
- Complete simulation tests
- Complete paper-trading period
- Validate accounting against broker statements
- Validate order/rejection behavior
- Validate market-session handling
- Validate kill switch
- Validate position reconciliation
- Validate duplicate-order prevention
- Validate network failure behavior
- Validate restart behavior
- Validate DEAD-state behavior
- Review current broker API rules
- Review current SEBI/exchange requirements
- Separate real-money credentials from development credentials

## Important
No real-money execution is implied by completing this phase. This is a readiness gate.

Real trading should use separately approved capital and a separately documented risk policy.
