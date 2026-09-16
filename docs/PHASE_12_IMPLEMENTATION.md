# Phase 12 — Autonomous Research Publication

## Implemented

`trading_lab.publication` establishes a programmatic gateway that evaluates experiments against strict rigorous criteria before automatically generating a markdown paper manuscript for human review.

Key features implemented:
- **`PublicationCriteria`**: Configurable thresholds (minimum trades, minimum win rate, max drawdowns) ensuring that only statistically robust findings advance to drafting.
- **Evidence Evaluator**: The `PublicationPipeline` dynamically queries the `experiments` ledger and rejects drafting if an experiment falls short of the `PublicationCriteria`.
- **Manuscript Generation**: For passing experiments, a markdown draft is generated with sections for Methodology, Results, and Reproducibility, tying the paper back to immutable SQLite records.
- **Audit Logging**: Successful draft generation emits a `PUBLICATION_DRAFTED` audit event.

## Limitations
- Actual statistical significance (e.g., p-values, Sharpe ratios) are mocked in Phase 12. The data science modules required for deep statistics should be plugged into the evaluation step during deployment.
- The system correctly refuses to bypass the human review step; every drafted manuscript includes a `PENDING` human review marker.

## Verification

`tests/test_phase12_publication.py` ensures that experiments below thresholds are firmly rejected, and passing experiments correctly generate a markdown draft accompanied by the required database audit event.

Run tests:
```sh
.venv/bin/python -m pytest
```
