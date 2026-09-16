# Phase 4 - Historical Data Pipeline

## Goal
Build a clean, reproducible historical-data pipeline for Indian instruments.

## Start small
Begin with a limited universe such as a major index and a small set of liquid equities.

Do not begin with thousands of symbols.

## Requirements
- Raw-data ingestion
- Validation
- Missing-data detection
- Duplicate detection
- Timestamp normalization
- Corporate-action handling
- Dataset versioning
- Data provenance
- Train/validation/test partitioning

## Anti-lookahead rules
The backtester must never expose future information to a strategy.

Store dataset versions and date boundaries for every experiment.

## Tests
- Duplicate bars detected.
- Missing bars flagged.
- Future rows cannot enter training data.
- Experiment records identify exact dataset versions.
