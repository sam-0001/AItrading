"""Deterministic Phase 2 paper execution. It has no broker or AI dependency."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from uuid import uuid4

from .domain import DomainError, SystemState, TerminalExperimentError
from .services import LabService
from .store import iso_now


PENNY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(PENNY, rounding=ROUND_HALF_UP)


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(StrEnum):
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    brokerage_rate: Decimal = Decimal("0.001")
    slippage_bps: Decimal = Decimal("10")
    daily_loss_limit: Decimal = Decimal("500.00")


@dataclass(frozen=True, slots=True)
class OrderRequest:
    symbol: str
    side: Side
    quantity: int
    requested_price: Decimal
    strategy_id: str
    strategy_version: int
    reason: str
    stop_loss: Decimal | None = None
    target_price: Decimal | None = None
    order_id: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    order_id: str
    status: OrderStatus
    fill_price: Decimal | None
    fees: Decimal
    slippage: Decimal
    reason: str | None = None


class VirtualBroker:
    """A deterministic execution simulator; every equity change calls LabService."""

    def __init__(self, lab: LabService, config: ExecutionConfig = ExecutionConfig()) -> None:
        self.lab, self.config = lab, config

    def available_cash(self) -> Decimal:
        self._ensure_cash_account()
        with self.lab.store.connection() as conn:
            return Decimal(conn.execute("SELECT available_cash FROM simulator_cash WHERE singleton=1").fetchone()["available_cash"])

    def position(self, symbol: str):
        with self.lab.store.connection() as conn:
            return conn.execute("SELECT * FROM simulator_positions WHERE symbol=?", (symbol,)).fetchone()

    def unrealized_pnl(self, symbol: str) -> Decimal:
        row = self.position(symbol)
        if row is None:
            return Decimal("0.00")
        return money((Decimal(row["last_price"]) - Decimal(row["average_cost"])) * row["quantity"] - Decimal(row["entry_fees"]))

    def submit_market_order(self, request: OrderRequest) -> ExecutionResult:
        self._ensure_cash_account()
        order_id = request.order_id or f"order_{uuid4()}"
        if self.lab.state() is SystemState.DEAD:
            raise TerminalExperimentError("DEAD experiments cannot accept orders")
        if request.quantity <= 0 or request.requested_price <= 0:
            return self._reject(order_id, request, "quantity and requested price must be positive")
        with self.lab.store.connection() as conn:
            existing = conn.execute("SELECT order_id FROM simulator_orders WHERE order_id=?", (order_id,)).fetchone()
        if existing:
            return self._reject(order_id, request, "duplicate order id", insert=False)
        multiplier = Decimal("1") + (self.config.slippage_bps / Decimal("10000")) * (Decimal("1") if request.side is Side.BUY else Decimal("-1"))
        fill = money(request.requested_price * multiplier)
        slippage = money(abs(fill - request.requested_price) * request.quantity)
        fees = money(fill * request.quantity * self.config.brokerage_rate)
        if request.side is Side.BUY:
            return self._buy(order_id, request, fill, fees, slippage)
        return self._sell(order_id, request, fill, fees, slippage)

    def process_price(self, symbol: str, price: Decimal) -> ExecutionResult | None:
        """Update a deterministic quote and execute a configured protective exit if hit."""
        row = self.position(symbol)
        if row is None or row["quantity"] == 0:
            return None
        previous = Decimal(row["last_price"])
        self._set_last_price(symbol, price)
        self.lab.record_accounting_entry(money((price - previous) * row["quantity"]), f"mark_{uuid4()}", "deterministic mark to market")
        if row["stop_loss"] is not None and price <= Decimal(row["stop_loss"]):
            return self.submit_market_order(OrderRequest(symbol, Side.SELL, row["quantity"], price, "risk_exit", 1, "stop_loss"))
        if row["target_price"] is not None and price >= Decimal(row["target_price"]):
            return self.submit_market_order(OrderRequest(symbol, Side.SELL, row["quantity"], price, "risk_exit", 1, "target"))
        return None

    def _ensure_cash_account(self) -> None:
        self.lab.initialize()
        initial_cash = self.lab.wallet().balance
        with self.lab.store.connection() as conn:
            row = conn.execute("SELECT singleton FROM simulator_cash WHERE singleton=1").fetchone()
            if row is None:
                conn.execute("INSERT INTO simulator_cash VALUES (1, ?, ?)", (str(initial_cash), iso_now()))

    def _buy(self, order_id, request, fill, fees, slippage) -> ExecutionResult:
        notional = money(fill * request.quantity)
        if self._daily_realized_pnl() <= -self.config.daily_loss_limit:
            return self._reject(order_id, request, "daily loss limit reached")
        if notional > self.lab.wallet().max_deployment:
            return self._reject(order_id, request, "maximum deployment exceeded")
        if notional + fees > self.available_cash():
            return self._reject(order_id, request, "insufficient available cash")
        row = self.position(request.symbol)
        old_quantity = 0 if row is None else row["quantity"]
        old_cost = Decimal("0") if row is None else Decimal(row["average_cost"]) * old_quantity
        new_quantity = old_quantity + request.quantity
        average_cost = money((old_cost + fill * request.quantity) / new_quantity)
        entry_fees = fees + (Decimal("0") if row is None else Decimal(row["entry_fees"]))
        entry_slippage = slippage + (Decimal("0") if row is None else Decimal(row["entry_slippage"]))
        with self.lab.store.connection() as conn:
            conn.execute("UPDATE simulator_cash SET available_cash=?,updated_at=? WHERE singleton=1", (str(money(self.available_cash() - notional - fees)), iso_now()))
            conn.execute("INSERT OR REPLACE INTO simulator_positions VALUES (?,?,?,?,?,?,?,?,?)", (request.symbol, new_quantity, str(average_cost), str(entry_fees), str(entry_slippage), str(request.requested_price), str(request.stop_loss) if request.stop_loss else None, str(request.target_price) if request.target_price else None, iso_now()))
            self._insert_order(conn, order_id, request, fill, fees, slippage, OrderStatus.FILLED, None)
        self.lab.record_accounting_entry(-(fees + slippage), order_id, "simulated entry fee and slippage")
        self.lab.store.append_event("SIMULATED_ORDER_FILLED", {"order_id": order_id, "side": "BUY", "symbol": request.symbol})
        return ExecutionResult(order_id, OrderStatus.FILLED, fill, fees, slippage)

    def _sell(self, order_id, request, fill, fees, slippage) -> ExecutionResult:
        row = self.position(request.symbol)
        if row is None or row["quantity"] < request.quantity:
            return self._reject(order_id, request, "insufficient position")
        quantity = row["quantity"]
        fraction = Decimal(request.quantity) / Decimal(quantity)
        entry_fees = money(Decimal(row["entry_fees"]) * fraction)
        entry_slippage = money(Decimal(row["entry_slippage"]) * fraction)
        marked_value = money(Decimal(row["last_price"]) * request.quantity)
        proceeds = money(fill * request.quantity - fees)
        pnl = money((fill - Decimal(row["average_cost"])) * request.quantity - entry_fees - fees)
        remaining = quantity - request.quantity
        with self.lab.store.connection() as conn:
            conn.execute("UPDATE simulator_cash SET available_cash=?,updated_at=? WHERE singleton=1", (str(money(self.available_cash() + proceeds)), iso_now()))
            if remaining:
                conn.execute("UPDATE simulator_positions SET quantity=?,entry_fees=?,entry_slippage=?,last_price=?,updated_at=? WHERE symbol=?", (remaining, str(money(Decimal(row["entry_fees"]) - entry_fees)), str(money(Decimal(row["entry_slippage"]) - entry_slippage)), str(request.requested_price), iso_now(), request.symbol))
            else:
                conn.execute("DELETE FROM simulator_positions WHERE symbol=?", (request.symbol,))
            self._insert_order(conn, order_id, request, fill, fees, slippage, OrderStatus.FILLED, None)
            conn.execute("INSERT INTO simulator_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (f"trade_{uuid4()}", order_id, request.symbol, request.quantity, row["average_cost"], str(fill), str(pnl), str(money(entry_fees + fees)), str(money(entry_slippage + slippage)), request.strategy_id, request.strategy_version, "entry", request.reason, iso_now()))
        self.lab.record_accounting_entry(money(proceeds - marked_value), order_id, "simulated exit settlement")
        self.lab.store.append_event("SIMULATED_ORDER_FILLED", {"order_id": order_id, "side": "SELL", "symbol": request.symbol, "pnl": str(pnl)})
        return ExecutionResult(order_id, OrderStatus.FILLED, fill, fees, slippage)

    def _set_last_price(self, symbol: str, price: Decimal) -> None:
        with self.lab.store.connection() as conn:
            conn.execute("UPDATE simulator_positions SET last_price=?,updated_at=? WHERE symbol=?", (str(price), iso_now(), symbol))

    def _daily_realized_pnl(self) -> Decimal:
        """UTC day boundary is explicit until Phase 3 supplies exchange-session dates."""
        today = iso_now()[:10]
        with self.lab.store.connection() as conn:
            rows = conn.execute("SELECT pnl FROM simulator_trades WHERE occurred_at LIKE ?", (f"{today}%",)).fetchall()
        return sum((Decimal(row["pnl"]) for row in rows), Decimal("0.00"))

    def _reject(self, order_id, request, reason, insert=True) -> ExecutionResult:
        if insert:
            with self.lab.store.connection() as conn:
                self._insert_order(conn, order_id, request, None, Decimal("0"), Decimal("0"), OrderStatus.REJECTED, reason)
            self.lab.store.append_event("SIMULATED_ORDER_REJECTED", {"order_id": order_id, "reason": reason})
        return ExecutionResult(order_id, OrderStatus.REJECTED, None, Decimal("0"), Decimal("0"), reason)

    @staticmethod
    def _insert_order(conn, order_id, request, fill, fees, slippage, status, rejection):
        conn.execute("INSERT INTO simulator_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (order_id, request.symbol, request.side.value, request.quantity, str(request.requested_price), str(fill) if fill is not None else None, str(fees), str(slippage), status.value, rejection, request.strategy_id, request.strategy_version, request.reason, iso_now()))
