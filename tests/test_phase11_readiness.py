import pytest
from trading_lab.readiness import LiveReadinessGate, ReadinessError
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.domain import SystemState


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


def test_readiness_gate_blocks_live(lab):
    gate = LiveReadinessGate(lab)
    
    with pytest.raises(ReadinessError) as exc:
        gate.evaluate_readiness()
        
    # By default, nothing is passed
    assert "SIMULATION_TESTS" in str(exc.value)
    assert "PAPER_TRADING" in str(exc.value)


def test_readiness_gate_manual_signoff(lab):
    gate = LiveReadinessGate(lab)
    
    # Sign off everything manually to simulate a bypass
    for item in gate.checklist:
        gate.manual_override_signoff(item.id, "boss_human")
        
    # Should not raise
    gate.evaluate_readiness()
    
    # Check audit
    with lab.store.connection() as conn:
        events = conn.execute("SELECT * FROM audit_events WHERE event_type='READINESS_SIGNOFF'").fetchall()
        assert len(events) == 10
