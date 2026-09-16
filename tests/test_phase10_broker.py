import pytest
from decimal import Decimal

from trading_lab.broker_adapter import AngelOnePaperAdapter, BrokerConfig, Environment
from trading_lab.simulator import OrderRequest, Side


def test_broker_paper_adapter_safety():
    config = BrokerConfig(env=Environment.PAPER)
    adapter = AngelOnePaperAdapter(config)
    
    # Live data should work
    bar = adapter.fetch_live_price("REL")
    assert bar is not None
    assert bar.symbol == "REL"
    
    # Paper order should return a paper ID without failing
    req = OrderRequest(
        symbol="REL",
        side=Side.BUY,
        quantity=10,
        requested_price=Decimal("100"),
        strategy_id="strat_01",
        strategy_version=1,
        reason="test"
    )
    order_id = adapter.submit_paper_order(req)
    assert order_id.startswith("paper_")


def test_broker_adapter_prevents_live():
    # Attempting to bypass the Environment enum directly or using invalid modes
    class FakeEnv:
        value = "LIVE"
        
    with pytest.raises(ValueError, match="is not permitted for safety reasons"):
        AngelOnePaperAdapter(BrokerConfig(env=FakeEnv()))
