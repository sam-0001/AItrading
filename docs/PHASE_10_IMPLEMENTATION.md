# Phase 10 — Broker API / Paper Integration

## Implemented

`trading_lab.broker_adapter` implements the safety boundary connecting the deterministic lab to the real world (via a broker API like Angel One), explicitly intercepting and neutralizing live execution.

Key features implemented:
- **Broker Adapter Interface**: A generic `BrokerAdapter` protocol defining `fetch_live_price` and `submit_paper_order`.
- **Environment Gating**: Added strict environment flags (`PAPER`, `LIVE_DISABLED`, `BACKTEST`). Any environment attempting to bypass these safety barriers raises a hard architectural exception.
- **Paper Interceptor**: The mocked `AngelOnePaperAdapter` successfully consumes the `OrderRequest` domain object and converts it to a paper transaction ID, preventing real-money transmission.

## Limitations
- Angel One SmartAPI specifics (authentication flows, websockets, ratelimits) are entirely simulated. The actual implementation requires the user to acquire correct API credentials and verify regulatory algo-trading compliance in India.
- Live trading is physically impossible in this module by design.

## Verification

`tests/test_phase10_broker.py` confirms that the adapter correctly issues paper IDs for execution and aggressively raises exceptions if the safety boundary environment is tampered with.

Run tests:
```sh
.venv/bin/python -m pytest
```
