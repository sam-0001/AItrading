# Phase 7 Prompt - Dynamic Virtual Capital

Implement Phase 7 only.

## Goal

Implement controlled virtual-capital scaling.

## Starting state

Virtual wallet = ₹1,000.

Initial maximum deployment = ₹500.

## Principle

Successful performance may earn greater permitted exposure.

Poor performance must reduce permitted exposure.

The AI must not decide capital limits.

## Tier engine

Implement a configurable deterministic tier engine.

Example configuration for development only:

- ₹1,000-₹1,499 -> ₹500 max deployment
- ₹1,500-₹2,499 -> ₹750
- ₹2,500-₹4,999 -> ₹1,250
- ₹5,000-₹9,999 -> ₹2,000

Do not treat these example values as proven optimal parameters.

## Promotion

Do not promote merely because the balance crossed a threshold.

Require configurable evidence such as:
- minimum trade count;
- minimum evaluation period;
- drawdown limit;
- performance after costs;
- robustness status.

## Demotion

When performance or balance deteriorates, reduce allowed exposure according to deterministic rules.

## Hard constraints

A trade must never exceed:
- available virtual cash;
- current deployment tier;
- position/risk limits.

## Death

If total wallet <= ₹0:
- immediately persist DEAD;
- disable further trading;
- prevent tier changes;
- prevent reset.

## Tests

Test:
- tier promotion;
- tier demotion;
- threshold boundaries;
- insufficient cash;
- death;
- restart after death;
- AI recommendation cannot override tier engine.
