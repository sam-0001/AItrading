# Phase 10 Prompt - Groww Paper Integration

Implement Phase 10 only.

## Goal

Integrate a broker adapter for market data and paper execution while keeping real-money execution disabled.

Groww may be used as the first broker adapter after verifying its current official API documentation, terms, authentication, limits, and supported capabilities.

## Architecture

Create a broker abstraction:

`BrokerAdapter`

Implement the Groww adapter behind that interface.

The rest of the trading engine must not depend directly on Groww-specific code.

## Required areas

Support where officially available:
- authentication;
- market data;
- instruments;
- orders;
- positions;
- account information;
- order status;
- error handling;
- rate limits.

## Safety

Default mode must be:

`LIVE_TRADING_DISABLED`

Supported modes should clearly distinguish:
- BACKTEST;
- PAPER;
- LIVE_DISABLED.

Do not create a hidden path that can send real orders.

## Secrets

Never hard-code:
- API keys;
- tokens;
- passwords.

Use environment/secret management.

## Paper reconciliation

Compare simulated state against incoming broker data where useful, without placing real orders.

## Tests

Mock all broker calls.

Prove:
- order calls are intercepted in paper mode;
- network failure fails safely;
- duplicate orders are prevented;
- authentication errors fail closed;
- no real order endpoint is reachable from the default test environment.

## Regulatory boundary

Before any future live execution, separately verify current Indian requirements and broker rules. Do not assume old documentation is still valid.
