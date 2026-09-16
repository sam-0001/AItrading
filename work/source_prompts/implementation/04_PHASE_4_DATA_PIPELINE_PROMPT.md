# Phase 4 Prompt - Historical Data Pipeline

Implement Phase 4 only.

## Goal

Create a reproducible historical-data pipeline for Indian-market research.

## Start small

Use a deliberately limited instrument universe for the first implementation.

The architecture must support expansion later.

## Requirements

Implement:
- raw data ingestion;
- validation;
- timestamp normalization;
- duplicate detection;
- missing-data detection;
- corporate-action handling where applicable;
- dataset versioning;
- provenance metadata;
- train/validation/test partitioning.

## Research integrity

Every dataset must have:
- dataset ID;
- version;
- source;
- retrieval time;
- instrument universe;
- date range;
- transformation history.

## Prevent look-ahead

The pipeline must make it difficult for an experiment to accidentally access future observations.

Training/validation/test boundaries must be explicit and stored.

## Tests

Prove:
- duplicates are detected;
- malformed data is rejected;
- missing data is flagged;
- future rows cannot enter a training partition;
- experiment records reference exact dataset versions.

## Do not implement

Do not add:
- AI strategy generation;
- live trading;
- Groww integration.

## Completion

Provide sample data fixtures and tests that make the pipeline reproducible without requiring external network access during tests.
