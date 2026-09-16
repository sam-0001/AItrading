from datetime import date, datetime, timezone
import zoneinfo
import pytest

from trading_lab.clock import MarketClock
from trading_lab.domain import SystemState

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


def test_naive_timestamp_rejected():
    clock = MarketClock()
    dt = datetime(2026, 1, 1, 10, 0)
    # MarketClock safely handles exceptions by returning ERROR_SAFE
    assert clock.get_market_state(dt) == SystemState.ERROR_SAFE


def test_weekend_handling():
    clock = MarketClock()
    # 2026-09-12 is a Saturday
    dt = datetime(2026, 9, 12, 10, 0, tzinfo=IST)
    assert clock.get_market_state(dt) == SystemState.MARKET_CLOSED


def test_holiday_handling():
    # 2026-01-26 is Republic Day (a holiday in India)
    holidays = {date(2026, 1, 26)}
    clock = MarketClock(holidays=holidays)
    dt = datetime(2026, 1, 26, 10, 0, tzinfo=IST)
    assert clock.get_market_state(dt) == SystemState.MARKET_CLOSED

    # Next day should be open (if it's a weekday)
    # 2026-01-27 is Tuesday
    dt2 = datetime(2026, 1, 27, 10, 0, tzinfo=IST)
    assert clock.get_market_state(dt2) == SystemState.MARKET_OPEN


def test_market_sessions_ist():
    clock = MarketClock()
    # 2026-09-16 is a Wednesday
    
    # 08:30 IST -> MARKET_CLOSED
    dt_closed_morning = datetime(2026, 9, 16, 8, 30, tzinfo=IST)
    assert clock.get_market_state(dt_closed_morning) == SystemState.MARKET_CLOSED
    
    # 09:10 IST -> PRE_MARKET
    dt_pre_market = datetime(2026, 9, 16, 9, 10, tzinfo=IST)
    assert clock.get_market_state(dt_pre_market) == SystemState.PRE_MARKET
    
    # 10:00 IST -> MARKET_OPEN
    dt_market_open = datetime(2026, 9, 16, 10, 0, tzinfo=IST)
    assert clock.get_market_state(dt_market_open) == SystemState.MARKET_OPEN
    
    # 15:20 IST -> MARKET_CLOSING
    dt_market_closing = datetime(2026, 9, 16, 15, 20, tzinfo=IST)
    assert clock.get_market_state(dt_market_closing) == SystemState.MARKET_CLOSING
    
    # 15:40 IST -> MARKET_CLOSED
    dt_closed_evening = datetime(2026, 9, 16, 15, 40, tzinfo=IST)
    assert clock.get_market_state(dt_closed_evening) == SystemState.MARKET_CLOSED


def test_market_sessions_utc_conversion():
    clock = MarketClock()
    # 2026-09-16 04:30:00 UTC is 10:00:00 IST (MARKET_OPEN)
    dt_utc = datetime(2026, 9, 16, 4, 30, tzinfo=timezone.utc)
    assert clock.get_market_state(dt_utc) == SystemState.MARKET_OPEN
