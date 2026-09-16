# Phase 5 - Strategy Laboratory

## Goal
Create a deterministic environment where strategies can be described, executed, and evaluated.

## Strategy interface
Each strategy should define:
- ID
- Version
- Hypothesis
- Required inputs
- Parameters
- Entry rules
- Exit rules
- Position-sizing rules
- Risk constraints

## Backtest outputs
At minimum:
- Total return
- Net P&L
- Number of trades
- Win rate
- Average win/loss
- Profit factor
- Maximum drawdown
- Exposure
- Fees
- Slippage
- Benchmark comparison

## Robustness
Support:
- Parameter perturbation
- Multiple market regimes
- Walk-forward testing
- Out-of-sample testing

## Critical rule
Do not select strategies solely by highest historical return.

Avoid multiple-testing/data-snooping traps by recording all experiments, including rejected ones.
