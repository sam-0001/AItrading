from __future__ import annotations

import logging
from typing import Protocol
from enum import Enum
from dataclasses import dataclass

from .simulator import OrderRequest, Side
from .data import Bar

logger = logging.getLogger(__name__)


class Environment(Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE_DISABLED = "LIVE_DISABLED"


@dataclass
class BrokerConfig:
    env: Environment
    api_key: str | None = None
    api_secret: str | None = None


class BrokerAdapter(Protocol):
    def fetch_live_price(self, symbol: str) -> Bar | None:
        ...

    def submit_paper_order(self, order: OrderRequest) -> str:
        ...


class AngelOnePaperAdapter:
    """Mock implementation for Phase 10 paper trading requirements using Angel One SmartAPI."""

    def __init__(self, config: BrokerConfig):
        self.config = config
        
        if self.config.env not in (Environment.PAPER, Environment.BACKTEST, Environment.LIVE_DISABLED):
            raise ValueError(f"Environment {self.config.env} is not permitted for safety reasons.")
            
        logger.info(f"Initialized Angel One adapter in {self.config.env.value} mode. LIVE ORDERS DISABLED.")

    def fetch_live_price(self, symbol: str) -> Bar | None:
        """Simulate fetching live price data from the broker API."""
        # For simulation, return a mock bar
        from datetime import datetime, timezone
        from decimal import Decimal
        return Bar(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            close=Decimal("102"),
            volume=500
        )

    def submit_paper_order(self, order: OrderRequest) -> str:
        """Simulate paper execution using broker live prices without real funds."""
        if self.config.env not in (Environment.PAPER, Environment.LIVE_DISABLED):
            raise ValueError("Live execution explicitly blocked by architecture constraints.")
            
        logger.info(f"[PAPER_ORDER_INTERCEPT] Intercepted {order.side} {order.quantity} of {order.symbol} at {order.requested_price}")
        return f"paper_{order.strategy_id}_{order.symbol}"
