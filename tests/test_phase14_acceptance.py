import pytest
from datetime import datetime, timezone
from decimal import Decimal

from trading_lab.domain import SystemState
from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.simulator import VirtualBroker, ExecutionConfig, OrderRequest, Side
from trading_lab.data import Bar, DatasetPartition
from trading_lab.strategy import BacktestEngine, Strategy
from trading_lab.reporting import DailyReporter, MockEmailSender
from trading_lab.capital import DynamicCapitalManager
from trading_lab.broker_adapter import AngelOnePaperAdapter, BrokerConfig, Environment
from trading_lab.readiness import LiveReadinessGate, ReadinessError
from trading_lab.publication import PublicationPipeline, PublicationCriteria


class EndToEndStrategy(Strategy):
    @property
    def hypothesis(self) -> str:
        return "End to end integration testing strategy."

    def on_bar(self, broker, bar_idx, partition):
        bar = partition.bars[bar_idx]
        if bar_idx == 0:
            req = OrderRequest(
                symbol=bar.symbol,
                side=Side.BUY,
                quantity=10,
                requested_price=bar.close,
                strategy_id=self.id,
                strategy_version=self.version,
                reason="e2e_entry"
            )
            broker.submit_market_order(req)
        elif bar_idx == 1:
            req = OrderRequest(
                symbol=bar.symbol,
                side=Side.SELL,
                quantity=10,
                requested_price=bar.close,
                strategy_id=self.id,
                strategy_version=self.version,
                reason="e2e_exit"
            )
            broker.submit_market_order(req)


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "test.db"
    store = SqliteStore(db_path)
    from trading_lab.migrations import apply_migrations
    with store.connection() as conn:
        apply_migrations(conn)
    return store


def test_full_acceptance_pipeline(store):
    """
    Simulates the entire lifecycle of the trading lab.
    """
    # 1. Foundation & Services
    lab = LabService(store)
    lab.initialize()
    lab.transition(SystemState.PRE_MARKET)
    lab.transition(SystemState.MARKET_OPEN)
    
    # 2. Broker & Simulator Integration
    config = BrokerConfig(env=Environment.PAPER)
    broker_adapter = AngelOnePaperAdapter(config)
    
    # Fake market data
    dt1 = datetime(2026, 9, 1, 10, tzinfo=timezone.utc)
    dt2 = datetime(2026, 9, 2, 10, tzinfo=timezone.utc)
    bars = [
        Bar("REL", dt1, Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"), 100),
        Bar("REL", dt2, Decimal("110"), Decimal("110"), Decimal("110"), Decimal("110"), 100),
    ]
    partition = DatasetPartition("REL", dt1, dt2, tuple(bars))
    
    # 3. Strategy & Backtest Execution
    # Note: Our EndToEndStrategy buys 10 @ 100 = 1000 cost. But max_deployment is 500 initially!
    # Let's override max_deployment for testing, or use lower quantity.
    # Actually, let's use quantity 5.
    class AdjustedE2EStrategy(EndToEndStrategy):
        def on_bar(self, broker, bar_idx, partition):
            bar = partition.bars[bar_idx]
            if bar_idx == 0:
                broker.submit_market_order(OrderRequest(bar.symbol, Side.BUY, 5, bar.close, self.id, self.version, "in"))
            elif bar_idx == 1:
                broker.submit_market_order(OrderRequest(bar.symbol, Side.SELL, 5, bar.close, self.id, self.version, "out"))
                
    broker = VirtualBroker(lab, ExecutionConfig(brokerage_rate=Decimal("0.0"), slippage_bps=Decimal("0")))
    engine = BacktestEngine(broker)
    strat = AdjustedE2EStrategy("e2e_strat", 1, {})
    
    # Run Experiment
    results = engine.run(strat, partition)
    assert results.total_trades == 1
    assert results.net_pnl == Decimal("50.00")
    
    # Record Experiment
    lab.store.create_immutable_experiment("exp_e2e", {
        "strategy_id": strat.id,
        "version": strat.version,
        "results": {
            "total_trades": results.total_trades,
            "win_rate": results.win_rate,
            "net_pnl": str(results.net_pnl)
        }
    })
    
    # 4. Dynamic Capital Evaluation
    manager = DynamicCapitalManager(lab, min_trades_required=1, min_win_rate=0.5)
    wallet = manager.evaluate_and_apply_tier()
    # It shouldn't promote since balance is 1050 (Tier 1 is 1000-1499). Max deployment stays 500.
    assert wallet.max_deployment == Decimal("500.00")
    
    # 5. Reporting
    lab.transition(SystemState.MARKET_CLOSING)
    lab.transition(SystemState.MARKET_CLOSED)
    
    email_sender = MockEmailSender()
    reporter = DailyReporter(lab, email_sender)
    reporter.send_reports()
    assert len(email_sender.sent_emails) == 1
    
    # 6. Publication Pipeline
    criteria = PublicationCriteria(min_trades=1, min_win_rate=0.9)
    pub_pipeline = PublicationPipeline(lab, criteria)
    draft = pub_pipeline.generate_manuscript("exp_e2e")
    assert "e2e_strat" in draft
    
    # 7. Readiness Gate (Will fail since PAPER_TRADES < 100)
    gate = LiveReadinessGate(lab)
    with pytest.raises(ReadinessError):
        gate.evaluate_readiness()
        
    # Sign off bypass
    for item in gate.checklist:
        gate.manual_override_signoff(item.id, "IntegrationTest")
    gate.evaluate_readiness() # Should pass now
