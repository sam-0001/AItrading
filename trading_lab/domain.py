from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


MONEY_ZERO = Decimal("0.00")
INITIAL_VIRTUAL_BALANCE = Decimal("1000.00")
INITIAL_MAX_DEPLOYMENT = Decimal("500.00")


class SystemState(StrEnum):
    INITIALIZING = "INITIALIZING"
    PRE_MARKET = "PRE_MARKET"
    MARKET_OPEN = "MARKET_OPEN"
    MARKET_CLOSING = "MARKET_CLOSING"
    MARKET_CLOSED = "MARKET_CLOSED"
    RESEARCH = "RESEARCH"
    DEAD = "DEAD"
    ERROR_SAFE = "ERROR_SAFE"


class DomainError(Exception):
    """A request violates a durable domain invariant."""


class InvalidStateTransition(DomainError):
    pass


class TerminalExperimentError(DomainError):
    pass


class ImmutableRecordError(DomainError):
    pass


@dataclass(frozen=True, slots=True)
class WalletSnapshot:
    balance: Decimal
    max_deployment: Decimal
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    event_type: str
    occurred_at: datetime
    payload_json: str
