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
        
        # Add default NSE/BSE holidays if none provided
        if not holidays:
            self._load_indian_holidays()

    def _load_indian_holidays(self):
        """Pre-loads known Indian Stock Market (NSE) holidays for 2024-2026."""
        # Note: Excluding weekends as they are handled dynamically
        nse_holidays = [
            # 2024
            date(2024, 1, 22),  # Special Holiday
            date(2024, 1, 26),  # Republic Day
            date(2024, 3, 8),   # Mahashivratri
            date(2024, 3, 25),  # Holi
            date(2024, 3, 29),  # Good Friday
            date(2024, 4, 11),  # Id-Ul-Fitr
            date(2024, 4, 17),  # Ram Navami
            date(2024, 5, 1),   # Maharashtra Day
            date(2024, 5, 20),  # General Elections
            date(2024, 6, 17),  # Bakri Id
            date(2024, 7, 17),  # Muharram
            date(2024, 8, 15),  # Independence Day
            date(2024, 10, 2),  # Mahatma Gandhi Jayanti
            date(2024, 11, 1),  # Diwali
            date(2024, 11, 15), # Gurunanak Jayanti
            date(2024, 12, 25), # Christmas
            
            # 2025
            date(2025, 2, 26),  # Mahashivratri
            date(2025, 3, 14),  # Holi
            date(2025, 3, 31),  # Id-Ul-Fitr (Tentative)
            date(2025, 4, 10),  # Mahavir Jayanti
            date(2025, 4, 14),  # Dr. Baba Saheb Ambedkar Jayanti
            date(2025, 4, 18),  # Good Friday
            date(2025, 5, 1),   # Maharashtra Day
            date(2025, 6, 6),   # Bakri Id (Tentative)
            date(2025, 8, 15),  # Independence Day
            date(2025, 8, 27),  # Ganesh Chaturthi
            date(2025, 10, 2),  # Mahatma Gandhi Jayanti
            date(2025, 10, 21), # Diwali
            date(2025, 11, 5),  # Gurunanak Jayanti
            date(2025, 12, 25), # Christmas
            
            # 2026
            date(2026, 1, 26),  # Republic Day
            date(2026, 2, 14),  # Mahashivratri
            date(2026, 3, 3),   # Holi
            date(2026, 3, 20),  # Id-Ul-Fitr (Tentative)
            date(2026, 3, 31),  # Mahavir Jayanti
            date(2026, 4, 3),   # Good Friday
            date(2026, 4, 14),  # Dr. Baba Saheb Ambedkar Jayanti
            date(2026, 5, 1),   # Maharashtra Day
            date(2026, 5, 27),  # Bakri Id (Tentative)
            date(2026, 8, 15),  # Independence Day
            date(2026, 9, 14),  # Ganesh Chaturthi
            date(2026, 10, 2),  # Mahatma Gandhi Jayanti
            date(2026, 11, 8),  # Diwali
            date(2026, 11, 24), # Gurunanak Jayanti
            date(2026, 12, 25), # Christmas
        ]
        for d in nse_holidays:
            self.holidays.add(d)

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
