import pytest
from decimal import Decimal
from uuid import uuid4

from trading_lab.reporting import DailyReporter, MockEmailSender
from trading_lab.domain import SystemState
from trading_lab.services import LabService
from trading_lab.store import SqliteStore, iso_now


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


def test_daily_report_sent(lab):
    lab.transition(SystemState.PRE_MARKET)
    lab.transition(SystemState.MARKET_OPEN)
    
    # Add a mock trade
    with lab.store.connection() as conn:
        conn.execute(
            "INSERT INTO simulator_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                f"trade_{uuid4()}", f"order_{uuid4()}", "REL", 10, "100", "110", 
                "100.00", "5.00", "0", "strat", 1, "entry", "exit", iso_now()
            )
        )
        
    mock_email = MockEmailSender()
    reporter = DailyReporter(lab, mock_email)
    
    reporter.send_reports()
    
    assert len(mock_email.sent_emails) == 1
    email = mock_email.sent_emails[0]
    assert email["subject"] == "Daily Research Report"
    assert "Net P&L: ₹100.00" in email["body"]
    assert "Total Trades: 1" in email["body"]
    assert "Fees Paid: ₹5.00" in email["body"]


def test_death_report_sent(lab):
    # Transition to DEAD
    lab.record_accounting_entry(Decimal("-1000.00"), "fatal_loss", "wiped out")
    
    assert lab.state() == SystemState.DEAD
    
    mock_email = MockEmailSender()
    reporter = DailyReporter(lab, mock_email)
    
    reporter.send_reports()
    
    assert len(mock_email.sent_emails) == 1
    email = mock_email.sent_emails[0]
    assert email["subject"] == "ALERT: Lab Dead"
    assert "!!! DEATH REPORT !!!" in email["body"]
