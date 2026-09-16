from datetime import datetime, timezone
from decimal import Decimal
import pytest

from trading_lab.ai_research import MockAIProvider, ResearchLoop
from trading_lab.data import Bar, DatasetPartition
from trading_lab.domain import SystemState
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.simulator import VirtualBroker, ExecutionConfig
from trading_lab.strategy import BacktestEngine


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


def test_ai_research_loop(lab):
    broker = VirtualBroker(lab, ExecutionConfig(brokerage_rate=Decimal("0.0"), slippage_bps=Decimal("0")))
    engine = BacktestEngine(broker)
    ai = MockAIProvider()
    
    loop = ResearchLoop(lab, engine, ai)
    
    dt1 = datetime(2026, 9, 1, 10, tzinfo=timezone.utc)
    dt2 = datetime(2026, 9, 2, 10, tzinfo=timezone.utc)
    bars = [
        Bar("REL", dt1, Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"), 100),
        Bar("REL", dt2, Decimal("110"), Decimal("110"), Decimal("110"), Decimal("110"), 100),
    ]
    partition = DatasetPartition("REL", dt1, dt2, tuple(bars))
    
    loop.run_experiment("exp_001", partition)
    
    # Verify immutable records
    with lab.store.connection() as conn:
        # Check strategy created
        strat = conn.execute("SELECT * FROM strategy_versions WHERE strategy_id='ai_strat_exp_001'").fetchone()
        assert strat is not None
        
        # Check experiment recorded
        exp = conn.execute("SELECT * FROM experiments WHERE experiment_id='exp_001'").fetchone()
        assert exp is not None
        
        # Check notes audit
        notes = conn.execute("SELECT * FROM audit_events WHERE event_type='AI_RESEARCH_NOTE'").fetchone()
        assert notes is not None
