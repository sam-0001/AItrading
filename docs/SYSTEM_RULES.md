# System Rules — Phase 1

1. The lab is simulation-only. Real money is always ₹0 in this phase.
2. Initial virtual balance is exactly ₹1,000.00; initial deployment ceiling is exactly ₹500.00.
3. `DEAD` is terminal. It cannot be reset, refilled, or transitioned out of, including after restart.
4. A balance of ₹0.00 or less immediately persists `DEAD`.
5. State and wallet changes are made only through `LabService`; future AI and strategy components are untrusted callers, not authorities.
6. Audit events, strategy versions, and experiments are append-only at the database level.
7. Phase 1 does not execute strategies or orders, ingest data, connect a broker, call AI, send email, or operate a scheduler.
