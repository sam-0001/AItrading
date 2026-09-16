# Phase 10 - Broker/API Paper Integration

## Goal
Connect to a broker API for live market data and simulated execution, while keeping real-money orders disabled.

## Requirements
- Broker adapter interface
- Authentication/secrets
- Market-data adapter
- Order adapter
- Position adapter
- Error/retry handling
- Rate-limit handling
- API audit logging

## Safety
The default environment must make real-money order placement impossible.

Example environments:
- `BACKTEST`
- `PAPER`
- `LIVE_DISABLED`

A separate, explicitly reviewed LIVE environment may be considered later.

## Broker
Groww can be evaluated as the broker adapter, but current API capabilities, pricing, authentication, terms, and applicable Indian algo-trading requirements must be verified from current official sources before implementation.

## Definition of done
Live market data can drive the same deterministic signal/risk/execution interfaces without sending real orders.
