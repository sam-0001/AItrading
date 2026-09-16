# Phase 7 - Dynamic Virtual Capital and Risk

## Goal
Allow successful simulated trading to increase permitted exposure while losses reduce it.

## Starting point
Total virtual wallet: ₹1,000.
Initial maximum deployment: ₹500.

## Design
Use deterministic risk tiers. Example only:

Tier 1: ₹1,000-₹1,499 wallet -> max deployment ₹500
Tier 2: ₹1,500-₹2,499 -> max deployment ₹750
Tier 3: ₹2,500-₹4,999 -> max deployment ₹1,250
Tier 4: ₹5,000-₹9,999 -> max deployment ₹2,000

Final values must be validated with experiments before production use.

## Promotion requirements
Do not promote solely because the wallet increased.

Require predefined conditions such as:
- Minimum number of trades
- Minimum evaluation period
- Drawdown ceiling
- Profitability after costs
- Stability/robustness checks

## Demotion
If performance deteriorates, permitted exposure decreases automatically.

## Hard limit
No trade may exceed:
- Available virtual cash
- Current risk-tier maximum
- Position/risk constraints

The AI can recommend a tier change but cannot enforce one.
