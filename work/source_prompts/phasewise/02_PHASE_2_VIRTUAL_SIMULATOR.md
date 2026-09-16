# Phase 2 - Deterministic Virtual Trading Simulator

## Goal
Build a realistic paper-trading engine with no AI and no broker API.

## Components
- Market data reader
- Order model
- Execution simulator
- Position manager
- Portfolio/accounting engine
- P&L engine
- Fees/charges model
- Slippage model
- Risk engine
- Trade ledger

## Required behavior
Support:
- Market buy/sell
- Limit orders where data permits
- Stop-loss
- Target exits
- Position tracking
- Cash accounting
- Realized/unrealized P&L
- Order status
- Rejected orders
- Transaction costs
- Slippage
- Position sizing
- Daily loss limits

## Accounting rule
Every simulated execution must update the wallet using the same deterministic accounting path.

Never directly mutate the wallet from a strategy.

## Death test
Create a deliberately losing strategy and verify:

₹1,000 -> losses -> ₹0 or below -> `DEAD`

Then restart the application and verify it remains `DEAD`.

## Definition of done
A complete trade can be reconstructed from the immutable event/trade ledger.
