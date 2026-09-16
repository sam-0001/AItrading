import pytest

from trading_lab.domain import DomainError
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.publication import PublicationPipeline, PublicationCriteria


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


def test_publication_pipeline(lab):
    # Setup mock experiment that passes criteria
    passing_exp = {
        "strategy_id": "test_strat",
        "version": 1,
        "results": {
            "total_trades": 600,
            "win_rate": 0.55,
            "net_pnl": "1000.00"
        }
    }
    lab.store.create_immutable_experiment("exp_pass", passing_exp)
    
    # Setup mock experiment that fails criteria
    failing_exp = {
        "strategy_id": "test_strat",
        "version": 2,
        "results": {
            "total_trades": 100,
            "win_rate": 0.50,
            "net_pnl": "10.00"
        }
    }
    lab.store.create_immutable_experiment("exp_fail", failing_exp)
    
    criteria = PublicationCriteria(min_trades=500, min_win_rate=0.52)
    pipeline = PublicationPipeline(lab, criteria)
    
    assert pipeline.evaluate_experiment("exp_pass") is True
    assert pipeline.evaluate_experiment("exp_fail") is False
    
    # Check draft generation
    draft = pipeline.generate_manuscript("exp_pass")
    assert "Autonomous Research Report: test_strat v1" in draft
    assert "PENDING" in draft
    
    # Check failure protection
    with pytest.raises(DomainError):
        pipeline.generate_manuscript("exp_fail")
        
    # Check audit log
    with lab.store.connection() as conn:
        events = conn.execute("SELECT * FROM audit_events WHERE event_type='PUBLICATION_DRAFTED'").fetchall()
        assert len(events) == 1
