# Phase 5 Prompt - Strategy Laboratory

Implement Phase 5 only.

## Goal

Create a deterministic strategy interface and research/backtesting laboratory.

## Strategy model

Each strategy must have:
- immutable strategy ID;
- version;
- hypothesis;
- description;
- inputs;
- parameters;
- entry rules;
- exit rules;
- position sizing;
- risk constraints.

## Backtesting

Build a deterministic engine that calculates:
- total return;
- net P&L;
- number of trades;
- win rate;
- average win;
- average loss;
- profit factor;
- maximum drawdown;
- exposure;
- fees;
- slippage;
- benchmark comparison.

## Robustness

Support:
- parameter perturbation;
- multiple periods;
- multiple instruments;
- walk-forward testing;
- out-of-sample testing.

## Critical rule

Never select a strategy only because it has the highest historical return.

Record every candidate, including failed candidates.

## Reproducibility

Given:
- same dataset version;
- same strategy version;
- same parameters;
- same cost/slippage assumptions;

the backtest must produce the same result.

## Tests

Create deterministic fixture strategies:
- known profitable;
- known losing;
- no-trade;
- high-turnover.

Verify metrics manually for small fixtures.

## Do not implement

Do not yet allow AI to autonomously create strategies.
