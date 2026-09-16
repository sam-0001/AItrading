from __future__ import annotations

from decimal import Decimal

import pytest

from trading_lab.domain import SystemState, TerminalExperimentError
from trading_lab.services import LabService
from trading_lab.simulator import (ExecutionConfig, OrderRequest, OrderStatus,
                                   Side, VirtualBroker)
from trading_lab.store import SqliteStore


@pytest.fixture
def broker(tmp_path):
    lab = LabService(SqliteStore(tmp_path / "simulator.sqlite3"))
    return VirtualBroker(lab, ExecutionConfig(brokerage_rate=Decimal("0.01"), slippage_bps=Decimal("100")))


def buy(symbol="ABC", quantity=2, price=Decimal("100"), **kwargs):
    return OrderRequest(symbol, Side.BUY, quantity, price, "fixture", 1, "entry", **kwargs)


def sell(symbol="ABC", quantity=2, price=Decimal("120"), **kwargs):
    return OrderRequest(symbol, Side.SELL, quantity, price, "fixture", 1, "exit", **kwargs)


def test_profitable_trade_updates_cash_wallet_and_immutable_ledger(broker):
    assert broker.submit_market_order(buy()).status is OrderStatus.FILLED
    result = broker.submit_market_order(sell())
    assert result.status is OrderStatus.FILLED
    assert broker.available_cash() == broker.lab.wallet().balance
    with broker.lab.store.connection() as conn:
        trade = conn.execute("SELECT pnl,fees,slippage FROM simulator_trades").fetchone()
        assert Decimal(trade["pnl"]) > 0
        assert conn.execute("SELECT COUNT(*) AS count FROM simulator_orders").fetchone()["count"] == 2


def test_loss_to_zero_makes_dead_and_survives_restart(tmp_path):
    path = tmp_path / "death.sqlite3"
    # Extreme, explicitly configured simulation costs make this a terminal-loss
    # fixture while still using the real execution/accounting path.
    broker = VirtualBroker(LabService(SqliteStore(path)), ExecutionConfig(brokerage_rate=Decimal("1"), slippage_bps=Decimal("0")))
    assert broker.submit_market_order(buy(quantity=5, price=Decimal("100"))).status is OrderStatus.FILLED
    assert broker.submit_market_order(sell(quantity=5, price=Decimal("0.01"))).status is OrderStatus.FILLED
    assert broker.lab.state() is SystemState.DEAD
    restarted = VirtualBroker(LabService(SqliteStore(path)))
    assert restarted.lab.state() is SystemState.DEAD
    with pytest.raises(TerminalExperimentError):
        restarted.submit_market_order(buy())


def test_insufficient_cash_and_max_deployment_are_rejected(broker):
    too_large = broker.submit_market_order(buy(quantity=6, price=Decimal("100")))
    assert too_large.status is OrderStatus.REJECTED
    assert too_large.reason == "maximum deployment exceeded"
    cash_short = VirtualBroker(broker.lab, ExecutionConfig(brokerage_rate=Decimal("1"), slippage_bps=Decimal("0")))
    assert cash_short.submit_market_order(buy(quantity=5, price=Decimal("100"))).status is OrderStatus.FILLED
    assert cash_short.submit_market_order(buy(symbol="XYZ", quantity=1, price=Decimal("100"))).reason == "insufficient available cash"


def test_stop_loss_and_target_exit_are_automatic_and_deterministic(broker):
    broker.submit_market_order(buy(stop_loss=Decimal("90"), target_price=Decimal("110")))
    stop = broker.process_price("ABC", Decimal("90"))
    assert stop is not None and stop.status is OrderStatus.FILLED
    broker.submit_market_order(buy(symbol="XYZ", stop_loss=Decimal("90"), target_price=Decimal("110")))
    target = broker.process_price("XYZ", Decimal("110"))
    assert target is not None and target.status is OrderStatus.FILLED


def test_fees_slippage_and_duplicate_ids_are_recorded(broker):
    request = buy(order_id="repeatable-order")
    result = broker.submit_market_order(request)
    assert result.fees == Decimal("2.02")
    assert result.slippage == Decimal("2.00")
    duplicate = broker.submit_market_order(request)
    assert duplicate.status is OrderStatus.REJECTED
    assert duplicate.reason == "duplicate order id"


def test_daily_loss_limit_blocks_new_entries(tmp_path):
    lab = LabService(SqliteStore(tmp_path / "daily-limit.sqlite3"))
    broker = VirtualBroker(lab, ExecutionConfig(brokerage_rate=Decimal("0"), slippage_bps=Decimal("0"), daily_loss_limit=Decimal("25")))
    broker.submit_market_order(buy(quantity=2, price=Decimal("100")))
    broker.submit_market_order(sell(quantity=2, price=Decimal("80")))
    blocked = broker.submit_market_order(buy(symbol="XYZ", quantity=1, price=Decimal("100")))
    assert blocked.status is OrderStatus.REJECTED
    assert blocked.reason == "daily loss limit reached"
