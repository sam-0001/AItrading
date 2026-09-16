# Phase 8 - Daily Reporting and Email

## Goal
Send a detailed end-of-day research/trading report automatically.

## Report sections
### Account
- Starting balance
- Ending balance
- Daily P&L
- Total return
- Drawdown
- Current risk tier
- Available capital

### Trading
- Number of trades
- Winners/losers
- Win rate
- Profit factor
- Average win/loss
- Largest win/loss
- Fees
- Slippage

### Trade-by-trade
For each trade:
- Symbol
- Timestamp
- Entry
- Exit
- Quantity
- P&L
- Strategy/version
- Entry reason
- Exit reason
- Market context

### Research
- What was learned
- What failed
- What worked
- New hypotheses
- Experiments completed
- Experiments rejected
- Strategies under evaluation
- Changes proposed

## Death report
If the wallet reaches ₹0 or below, immediately generate a dedicated final report explaining:
- Last balance
- Timeline to death
- Largest losses
- Strategies responsible
- Drawdown history
- Last active strategy versions
- Relevant experiments

The report must not restart the experiment.
