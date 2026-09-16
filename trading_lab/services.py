from __future__ import annotations

from decimal import Decimal

from .domain import (INITIAL_MAX_DEPLOYMENT, INITIAL_VIRTUAL_BALANCE, MONEY_ZERO,
                     DomainError, InvalidStateTransition, SystemState,
                     TerminalExperimentError, WalletSnapshot)
from .store import SqliteStore, iso_now


ALLOWED_TRANSITIONS: dict[SystemState, set[SystemState]] = {
    SystemState.INITIALIZING: {SystemState.PRE_MARKET, SystemState.MARKET_CLOSED, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.PRE_MARKET: {SystemState.MARKET_OPEN, SystemState.MARKET_CLOSED, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.MARKET_OPEN: {SystemState.MARKET_CLOSING, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.MARKET_CLOSING: {SystemState.MARKET_CLOSED, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.MARKET_CLOSED: {SystemState.RESEARCH, SystemState.PRE_MARKET, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.RESEARCH: {SystemState.PRE_MARKET, SystemState.MARKET_CLOSED, SystemState.ERROR_SAFE, SystemState.DEAD},
    SystemState.ERROR_SAFE: {SystemState.INITIALIZING, SystemState.MARKET_CLOSED, SystemState.DEAD},
    SystemState.DEAD: set(),
}


class LabService:
    """Only authoritative mutation API for state and virtual accounting."""

    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def initialize(self) -> None:
        initialized = False
        with self.store.connection() as conn:
            row = conn.execute("SELECT state FROM system_state WHERE singleton=1").fetchone()
            if row is None:
                conn.execute("INSERT INTO system_state VALUES (1, ?, ?)", (SystemState.INITIALIZING.value, iso_now()))
                conn.execute("INSERT INTO wallet VALUES (1, ?, ?, ?)", (str(INITIAL_VIRTUAL_BALANCE), str(INITIAL_MAX_DEPLOYMENT), iso_now()))
                initialized = True
        if initialized:
            self.store.append_event("LAB_INITIALIZED", {"virtual_balance": str(INITIAL_VIRTUAL_BALANCE), "max_deployment": str(INITIAL_MAX_DEPLOYMENT)})

    def state(self) -> SystemState:
        self.initialize()
        with self.store.connection() as conn:
            row = conn.execute("SELECT state FROM system_state WHERE singleton=1").fetchone()
        return SystemState(row["state"])

    def wallet(self) -> WalletSnapshot:
        self.initialize()
        wallet = self.store.wallet()
        assert wallet is not None
        return wallet

    def transition(self, target: SystemState, actor: str = "system") -> None:
        current = self.state()
        if current is SystemState.DEAD:
            raise TerminalExperimentError("DEAD is terminal and cannot be changed")
        if target not in ALLOWED_TRANSITIONS[current]:
            raise InvalidStateTransition(f"{current} -> {target} is not allowed")
        with self.store.connection() as conn:
            conn.execute("UPDATE system_state SET state=?, updated_at=? WHERE singleton=1", (target.value, iso_now()))
        self.store.append_event("STATE_CHANGED", {"from": current.value, "to": target.value, "actor": actor})

    def record_accounting_entry(self, amount: Decimal, reference: str, reason: str) -> WalletSnapshot:
        """The sole Phase 1 wallet mutation path; later simulator calls this service."""
        if not reference.strip() or not reason.strip():
            raise DomainError("accounting entries require a reference and reason")
        if self.state() is SystemState.DEAD:
            raise TerminalExperimentError("DEAD experiments cannot accept accounting entries")
        with self.store.connection() as conn:
            prior = conn.execute("SELECT balance,max_deployment FROM wallet WHERE singleton=1").fetchone()
            balance = Decimal(prior["balance"]) + amount
            conn.execute("UPDATE wallet SET balance=?, updated_at=? WHERE singleton=1", (str(balance), iso_now()))
        self.store.append_event("ACCOUNTING_ENTRY", {"amount": str(amount), "reference": reference, "reason": reason, "balance": str(balance)})
        if balance <= MONEY_ZERO:
            self._declare_dead(reference)
        return self.wallet()

    def update_max_deployment(self, new_max: Decimal, reason: str) -> WalletSnapshot:
        if self.state() is SystemState.DEAD:
            raise TerminalExperimentError("DEAD experiments cannot update deployment tiers")
        if new_max <= MONEY_ZERO:
            raise DomainError("max deployment must be positive")
        
        with self.store.connection() as conn:
            conn.execute("UPDATE wallet SET max_deployment=?, updated_at=? WHERE singleton=1", (str(new_max), iso_now()))
            
        self.store.append_event("MAX_DEPLOYMENT_UPDATED", {"new_max": str(new_max), "reason": reason})
        return self.wallet()

    def _declare_dead(self, reference: str) -> None:
        current = self.state()
        if current is SystemState.DEAD:
            return
        with self.store.connection() as conn:
            conn.execute("UPDATE system_state SET state=?, updated_at=? WHERE singleton=1", (SystemState.DEAD.value, iso_now()))
        self.store.append_event("EXPERIMENT_DEAD", {"reference": reference, "terminal": True})
