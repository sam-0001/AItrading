from decimal import Decimal
import pytest
from uuid import uuid4

from trading_lab.capital import DynamicCapitalManager
from trading_lab.domain import SystemState, DomainError
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
    lab_service.transition(SystemState.PRE_MARKET)
    lab_service.transition(SystemState.MARKET_OPEN)
    return lab_service


def add_mock_trades(lab, count: int, pnl_each: Decimal):
    with lab.store.connection() as conn:
        for i in range(count):
            conn.execute(
                "INSERT INTO simulator_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    f"trade_{uuid4()}", f"order_{uuid4()}", "REL", 10, "100", "110", 
                    str(pnl_each), "0", "0", "strat", 1, "entry", "exit", iso_now()
                )
            )


def test_dynamic_capital_promotion_denied_no_trades(lab):
    # Bump wallet artificially to Tier 2 boundary
    lab.record_accounting_entry(Decimal("600.00"), "mock_bump", "bump")
    assert lab.wallet().balance == Decimal("1600.00")
    
    manager = DynamicCapitalManager(lab, min_trades_required=10)
    wallet = manager.evaluate_and_apply_tier()
    
    # Should be denied because no trades exist
    assert wallet.max_deployment == Decimal("500.00")


def test_dynamic_capital_promotion_approved(lab):
    # Bump wallet artificially to Tier 2 boundary
    lab.record_accounting_entry(Decimal("600.00"), "mock_bump", "bump")
    
    # Add 10 winning trades to satisfy promotion rules
    add_mock_trades(lab, 10, Decimal("50.00"))
    
    manager = DynamicCapitalManager(lab, min_trades_required=10, min_win_rate=0.4)
    wallet = manager.evaluate_and_apply_tier()
    
    # Tier 2 approved
    assert wallet.max_deployment == Decimal("750.00")


def test_dynamic_capital_demotion_automatic(lab):
    # Bump to Tier 2 and approve
    lab.record_accounting_entry(Decimal("600.00"), "mock_bump", "bump")
    add_mock_trades(lab, 10, Decimal("50.00"))
    manager = DynamicCapitalManager(lab, min_trades_required=10, min_win_rate=0.4)
    wallet = manager.evaluate_and_apply_tier()
    assert wallet.max_deployment == Decimal("750.00")
    
    # Incur heavy loss to fall back to Tier 1
    lab.record_accounting_entry(Decimal("-500.00"), "mock_loss", "loss")
    assert lab.wallet().balance == Decimal("1100.00")
    
    # Demotion should happen automatically regardless of trade count/win rate
    wallet = manager.evaluate_and_apply_tier()
    assert wallet.max_deployment == Decimal("500.00")


def test_lab_service_update_max_deployment_guard(lab):
    with pytest.raises(DomainError):
        lab.update_max_deployment(Decimal("-100.00"), "invalid")
