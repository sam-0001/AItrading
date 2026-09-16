from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict

from .data import DatasetPartition
from .simulator import VirtualBroker, OrderRequest, Side

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BacktestResult:
    strategy_id: str
    strategy_version: int
    net_pnl: Decimal
    total_trades: int
    win_rate: float
    max_drawdown: Decimal
    fees: Decimal
    slippage: Decimal


class Strategy(ABC):
    """Base interface for all executable trading strategies."""

    def __init__(self, id: str, version: int, params: Dict[str, Any]):
        self.id = id
        self.version = version
        self.params = params

    @property
    @abstractmethod
    def hypothesis(self) -> str:
        pass

    @abstractmethod
    def on_bar(self, broker: VirtualBroker, bar_idx: int, partition: DatasetPartition) -> None:
        """Evaluate entry, exit, position sizing, and risk constraints."""
        pass


class BacktestEngine:
    """Deterministic environment to evaluate strategies without lookahead traps."""

    def __init__(self, broker: VirtualBroker):
        self.broker = broker
        # Tracks equity curve for drawdown calculation
        self.equity_curve: list[Decimal] = []

    def run(self, strategy: Strategy, partition: DatasetPartition) -> BacktestResult:
        logger.info("Starting backtest for %s v%s", strategy.id, strategy.version)
        
        initial_equity = self.broker.lab.wallet().balance
        self.equity_curve = [initial_equity]

        # Iterate through the partition securely
        for i, bar in enumerate(partition.bars):
            if self.broker.lab.state() == "DEAD":
                logger.warning("Lab state is DEAD. Stopping backtest.")
                break
                
            # Update quotes deterministically for stops/targets
            self.broker.process_price(bar.symbol, bar.close)

            # Strategy decision logic
            strategy.on_bar(self.broker, i, partition)

            # Record equity
            current_equity = self.broker.lab.wallet().balance + self.broker.unrealized_pnl(bar.symbol)
            self.equity_curve.append(current_equity)

        return self._evaluate_results(strategy.id, strategy.version, initial_equity)

    def _evaluate_results(self, strategy_id: str, version: int, initial_equity: Decimal) -> BacktestResult:
        with self.broker.lab.store.connection() as conn:
            trades = conn.execute(
                "SELECT * FROM simulator_trades WHERE strategy_id=? AND strategy_version=?",
                (strategy_id, version)
            ).fetchall()

        net_pnl = Decimal("0.00")
        wins = 0
        total_fees = Decimal("0.00")
        total_slippage = Decimal("0.00")

        for t in trades:
            pnl = Decimal(t["pnl"])
            net_pnl += pnl
            total_fees += Decimal(t["fees"])
            total_slippage += Decimal(t["slippage"])
            if pnl > 0:
                wins += 1

        total_trades = len(trades)
        win_rate = (wins / total_trades) if total_trades > 0 else 0.0

        max_dd = Decimal("0.00")
        peak = self.equity_curve[0]
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = peak - eq
            if dd > max_dd:
                max_dd = dd

        return BacktestResult(
            strategy_id=strategy_id,
            strategy_version=version,
            net_pnl=net_pnl,
            total_trades=total_trades,
            win_rate=win_rate,
            max_drawdown=max_dd,
            fees=total_fees,
            slippage=total_slippage
        )
