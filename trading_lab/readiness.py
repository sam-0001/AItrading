from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from .services import LabService

logger = logging.getLogger(__name__)


class ReadinessError(Exception):
    """Raised when the system fails the strict Live Readiness Gate."""
    pass


@dataclass
class ChecklistItem:
    id: str
    description: str
    is_passed: bool = False


class LiveReadinessGate:
    """Evaluates Phase 11 prerequisites before Live execution can even be considered."""

    def __init__(self, lab: LabService):
        self.lab = lab
        self.checklist = [
            ChecklistItem("SIMULATION_TESTS", "Complete simulation tests"),
            ChecklistItem("PAPER_TRADING", "Complete paper-trading period"),
            ChecklistItem("ACCOUNTING_MATCH", "Validate accounting against broker statements"),
            ChecklistItem("KILL_SWITCH", "Validate kill switch"),
            ChecklistItem("POSITION_RECON", "Validate position reconciliation"),
            ChecklistItem("DUP_PREVENTION", "Validate duplicate-order prevention"),
            ChecklistItem("NETWORK_FAIL", "Validate network failure behavior"),
            ChecklistItem("DEAD_STATE", "Validate DEAD-state behavior"),
            ChecklistItem("SEBI_COMPLIANCE", "Review current SEBI/exchange requirements"),
            ChecklistItem("SECRETS_SEPARATION", "Separate real-money credentials from development credentials")
        ]

    def evaluate_readiness(self) -> None:
        """
        Runs programmatic checks to verify if the lab is ready for live mode.
        If any checklist item is unsatisfied, it raises a ReadinessError.
        """
        logger.info("Evaluating Live Readiness Gate...")
        
        # 1. Programmatic Check: Has paper trading produced enough trades?
        with self.lab.store.connection() as conn:
            trades = conn.execute("SELECT COUNT(*) as count FROM simulator_trades").fetchone()
            if trades and trades["count"] > 100:
                self._mark_passed("PAPER_TRADING")
                
        # 2. Programmatic Check: Has DEAD state been audited?
        with self.lab.store.connection() as conn:
            dead_events = conn.execute("SELECT COUNT(*) as count FROM audit_events WHERE event_type='EXPERIMENT_DEAD'").fetchone()
            if dead_events and dead_events["count"] > 0:
                self._mark_passed("DEAD_STATE")
                
        # For simulation of Phase 11, we will hardcode the rest as 'Not Passed' by default
        # because a human needs to manually verify SEBI rules and broker statements.
        
        failed = [item for item in self.checklist if not item.is_passed]
        if failed:
            missing = ", ".join(item.id for item in failed)
            raise ReadinessError(f"Live readiness gate failed. Outstanding checklist items: {missing}")
            
        logger.warning("LIVE READINESS GATE PASSED. (Mocked)")

    def _mark_passed(self, item_id: str) -> None:
        for item in self.checklist:
            if item.id == item_id:
                item.is_passed = True
                break

    def manual_override_signoff(self, item_id: str, signed_by: str) -> None:
        """Human operator signing off on a manual check."""
        self._mark_passed(item_id)
        self.lab.store.append_event(
            "READINESS_SIGNOFF",
            {"item_id": item_id, "signed_by": signed_by}
        )
