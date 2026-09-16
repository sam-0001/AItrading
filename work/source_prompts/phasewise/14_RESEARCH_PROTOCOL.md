# Research Protocol

## Purpose
Prevent overfitting, hindsight bias, data leakage, and uncontrolled strategy selection.

## Required experiment record
Every experiment must record:
- Experiment ID
- Date/time
- Dataset version
- Instrument universe
- Training period
- Validation period
- Out-of-sample period
- Strategy version
- Parameters
- Costs/slippage assumptions
- Metrics
- Benchmark
- Decision
- AI/model metadata where applicable

## Dataset separation
No future information may enter training.

## Multiple testing
Record every tested candidate, including failed candidates.

Do not present the best result as representative if many alternatives were tested.

## Robustness
Where applicable test:
- Parameter perturbation
- Different market regimes
- Different instruments
- Different time periods
- Cost sensitivity
- Slippage sensitivity

## Research conclusion
A profitable backtest is evidence to investigate, not proof that future performance will continue.

## Publication
Publication criteria must be defined before evaluating the final candidate.
