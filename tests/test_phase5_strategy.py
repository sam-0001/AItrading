from datetime import datetime, timezone
from decimal import Decimal
import os
import sqlite3
import pytest

from trading_lab.data import Bar, DatasetPartition
from trading_lab.domain import SystemState
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.simulator import VirtualBroker, OrderRequest, Side, ExecutionConfig
from trading_lab.strategy import Strategy, BacktestEngine


class DummyStrategy(Strategy):
    @property
    def hypothesis(self) -> str:
        return "Buy on first bar, sell on second bar."

    def on_bar(self, broker: VirtualBroker, bar_idx: int, partition: DatasetPartition) -> None:
        bar = partition.bars[bar_idx]
        if bar_idx == 0:
            req = OrderRequest(
                symbol=bar.symbol,
                side=Side.BUY,
                quantity=5,
                requested_price=bar.close,
                strategy_id=self.id,
                strategy_version=self.version,
                reason="entry"
            )
            broker.submit_market_order(req)
        elif bar_idx == 1:
            req = OrderRequest(
                symbol=bar.symbol,
                side=Side.SELL,
                quantity=5,
                requested_price=bar.close,
                strategy_id=self.id,
                strategy_version=self.version,
                reason="exit"
            )
            broker.submit_market_order(req)

@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "test.db"
    store = SqliteStore(db_path)
    # Apply schema
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


def test_strategy_backtest(lab):
    broker = VirtualBroker(lab, ExecutionConfig(brokerage_rate=Decimal("0.0"), slippage_bps=Decimal("0")))
    engine = BacktestEngine(broker)
    
    dt1 = datetime(2026, 9, 1, 10, tzinfo=timezone.utc)
    dt2 = datetime(2026, 9, 2, 10, tzinfo=timezone.utc)
    
    bars = [
        Bar("REL", dt1, Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"), 100),
        Bar("REL", dt2, Decimal("110"), Decimal("110"), Decimal("110"), Decimal("110"), 100),
    ]
    partition = DatasetPartition("REL", dt1, dt2, tuple(bars))
    
    strategy = DummyStrategy("dummy_01", 1, {})
    result = engine.run(strategy, partition)
    
    # Buy 5 at 100 = cost 500. Sell 5 at 110 = 550. P&L = +50
    assert result.total_trades == 1
    assert result.net_pnl == Decimal("50.00")
    assert result.win_rate == 1.0
