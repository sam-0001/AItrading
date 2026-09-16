# AI Trading Lab - Master Plan

## Objective
Build a continuously running quantitative research and simulated trading system for Indian markets.

The system starts with a ₹1,000 virtual wallet and initially permits a maximum of ₹500 deployment. It trades only simulated capital during the learning stages.

## Core principles
- Simulation first. No real-money execution in the initial phases.
- The AI researches and proposes hypotheses; deterministic engines calculate results and enforce risk.
- Every strategy, experiment, parameter set, signal, and trade is versioned and permanently logged.
- Historical results cannot be rewritten.
- Backtests must include realistic transaction costs and slippage.
- Out-of-sample and walk-forward validation are mandatory before a strategy can advance.
- Virtual capital may grow or shrink according to deterministic rules.
- Larger exposure must be earned through predefined performance criteria, not AI discretion.
- Deteriorating performance must reduce permitted exposure.
- If total virtual wallet balance reaches ₹0 or below, the experiment enters an irreversible `DEAD` state.
- `DEAD` cannot be reset, refilled, or bypassed by the AI or by a service restart.
- Research history remains available after death.
- Daily reports are sent by email.
- Any future real-money integration must be isolated from the research wallet and separately reviewed for current broker/API and regulatory requirements.

## Phase order
1. Foundation and rules
2. Deterministic virtual trading simulator
3. Indian market calendar/session engine
4. Historical data pipeline
5. Strategy laboratory
6. AI research loop
7. Dynamic virtual capital/risk tiers
8. Daily reporting and email
9. VPS deployment and reliability
10. Broker/API paper integration
11. Real-money readiness review
12. Autonomous research-paper generation with human review before publication

## Definition of done
A phase is complete only when its acceptance tests pass. Do not implement later phases early just to make a demo look complete.
