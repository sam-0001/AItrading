from __future__ import annotations

import logging
import zoneinfo
from datetime import date, datetime, time

from .domain import SystemState

logger = logging.getLogger(__name__)

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

PRE_MARKET_START = time(9, 0)
MARKET_OPEN_START = time(9, 15)
MARKET_CLOSING_START = time(15, 15)
MARKET_CLOSED_START = time(15, 30)


class MarketClock:
    """Timezone-safe Indian exchange calendar and session abstraction."""

    def __init__(self, holidays: set[date] | None = None):
        """
        Initialize the MarketClock with an optional set of known holidays.
        """
        self.holidays = holidays or set()

    def is_trading_day(self, d: date) -> bool:
        """Return True if the given date is a trading day (not weekend or holiday)."""
        if d.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        if d in self.holidays:
            return False
        return True

    def get_market_state(self, timestamp: datetime) -> SystemState:
        """
        Return the expected SystemState for a given timezone-aware timestamp.
        Falls back to MARKET_CLOSED if there is uncertainty or missing data.
        """
        try:
            if timestamp.tzinfo is None:
                raise ValueError("timestamp must be timezone-aware")

            dt_ist = timestamp.astimezone(IST)
            d = dt_ist.date()
            t = dt_ist.time()

            if not self.is_trading_day(d):
                return SystemState.MARKET_CLOSED

            if t < PRE_MARKET_START:
                return SystemState.MARKET_CLOSED
            elif t < MARKET_OPEN_START:
                return SystemState.PRE_MARKET
            elif t < MARKET_CLOSING_START:
                return SystemState.MARKET_OPEN
            elif t < MARKET_CLOSED_START:
                return SystemState.MARKET_CLOSING
            else:
                return SystemState.MARKET_CLOSED

        except Exception as e:
            logger.error("Error evaluating market state: %s", e)
            return SystemState.ERROR_SAFE
