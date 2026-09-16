# Phase 2 Prompt - Virtual Trading Simulator

Implement Phase 2 only.

## Goal

Build a deterministic simulated broker/execution engine around the Phase 1 wallet.

No AI and no real broker.

## Required functionality

Implement:
- market buy;
- market sell;
- position tracking;
- cash accounting;
- realized P&L;
- unrealized P&L;
- order lifecycle;
- rejected orders;
- stop loss;
- target exit;
- position sizing;
- maximum deployment;
- transaction costs;
- slippage;
- trade ledger.

## Accounting

Never allow strategies to directly alter balances.

All balance changes must go through one deterministic accounting path.

Every execution must record:
- order ID;
- trade ID;
- symbol;
- side;
- quantity;
- requested price;
- simulated fill price;
- timestamp;
- fees;
- slippage;
- strategy/version;
- P&L.

## ₹0 death test

Create a test strategy that loses repeatedly.

Prove:

₹1,000 -> losses -> ₹0 or below -> `DEAD`.

Then restart the application.

Prove:
- wallet remains dead;
- no new orders are accepted;
- no automatic refill occurs;
- historical trades remain available.

## Realism

Do not claim simulated execution equals real execution.

Make cost/slippage assumptions configurable and recorded with every experiment.

## Tests

Include:
- profitable trade;
- losing trade;
- insufficient cash;
- excessive deployment;
- stop loss;
- target;
- fees;
- slippage;
- duplicate order handling;
- DEAD behavior;
- restart after death.

## Do not build

Do not add:
- AI;
- Groww;
- live market data;
- autonomous strategy generation.

## Completion

Run all tests and provide a concise implementation report.
