import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from trading_lab.domain import SystemState
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.scheduler import LabScheduler


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "test.db"
    store = SqliteStore(db_path)
    from trading_lab.migrations import apply_migrations
    with store.connection() as conn:
        apply_migrations(conn)
    return store


@pytest.fixture
def lab(store):
    lab_service = LabService(store)
    lab_service.initialize()
    return lab_service


def test_scheduler_transitions(lab):
    mock_clock = Mock()
    mock_clock.get_market_state.return_value = SystemState.PRE_MARKET
    
    mock_reporter = Mock()
    
    scheduler = LabScheduler(lab, mock_clock, mock_reporter)
    
    # Tick 1: Transition to PRE_MARKET
    scheduler._tick()
    assert lab.state() == SystemState.PRE_MARKET
    
    # Tick 2: Transition to MARKET_OPEN
    mock_clock.get_market_state.return_value = SystemState.MARKET_OPEN
    scheduler._tick()
    assert lab.state() == SystemState.MARKET_OPEN
    
    # Tick 3: Transition to MARKET_CLOSING
    mock_clock.get_market_state.return_value = SystemState.MARKET_CLOSING
    scheduler._tick()
    assert lab.state() == SystemState.MARKET_CLOSING
    
    # Tick 4: Transition to MARKET_CLOSED and run EOD
    mock_clock.get_market_state.return_value = SystemState.MARKET_CLOSED
    scheduler._tick()
    
    # EOD should transition to RESEARCH
    assert lab.state() == SystemState.RESEARCH
    mock_reporter.send_reports.assert_called_once()
