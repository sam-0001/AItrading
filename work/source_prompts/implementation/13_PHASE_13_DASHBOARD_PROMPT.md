# Phase 13 Prompt - Research and Trading Dashboard

Implement Phase 13 only.

## Goal

Create a dashboard that lets the operator inspect the autonomous research lab without manually controlling the trading logic.

## Dashboard sections

### System
- current state;
- market state;
- uptime;
- health;
- last successful data update;
- last research run.

### Virtual wallet
- balance;
- available capital;
- current deployment limit;
- P&L;
- drawdown;
- lifetime return;
- DEAD status.

### Trades
- open positions;
- completed trades;
- strategy/version;
- entry/exit;
- P&L;
- costs;
- slippage.

### Strategies
- active;
- candidate;
- paper;
- rejected;
- dead/retired;
- versions.

### Research
- experiments;
- hypotheses;
- validation status;
- robustness;
- charts;
- research-paper candidates.

## Safety

Dashboard actions must not bypass:
- risk engine;
- state machine;
- DEAD rule.

Do not expose destructive controls without explicit authorization.

## Read-only first

Prefer a read-only dashboard for the first implementation.

Do not add manual trading controls unless explicitly requested later.
