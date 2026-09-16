# Phase 8 Prompt - Daily Reporting

Implement Phase 8 only.

## Goal

Generate and send a detailed daily email report automatically after the simulated trading session.

## Report

Include:

### Account
- starting balance;
- ending balance;
- daily P&L;
- total return;
- drawdown;
- risk tier;
- available capital.

### Trading
- trade count;
- winners;
- losers;
- win rate;
- profit factor;
- average win/loss;
- largest win/loss;
- fees;
- slippage.

### Every trade
Include:
- symbol;
- entry;
- exit;
- quantity;
- P&L;
- strategy/version;
- entry reason;
- exit reason;
- market context.

### Research
Include:
- what the system learned;
- what failed;
- what worked;
- hypotheses created;
- experiments completed;
- strategies rejected;
- strategies under evaluation;
- proposed next experiments.

## Death report

If the wallet reaches ₹0 or below, generate a final report containing:
- final balance;
- time of death;
- path to death;
- largest losses;
- strategy versions involved;
- drawdown;
- relevant experiments;
- lessons.

Do not restart the experiment after sending the report.

## Reliability

Email failure must not corrupt trading/accounting state.

Store report generation status and allow safe retry.

## Tests

Use a mock email provider.

Verify:
- correct daily figures;
- all trades included;
- death report generated;
- duplicate sends avoided where required;
- email failure does not modify wallet.
