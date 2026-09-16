from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from .services import LabService
from .store import SqliteStore

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generates a read-only static HTML observability dashboard."""

    def __init__(self, lab: LabService):
        self.lab = lab

    def generate_html(self) -> str:
        """
        Reads immutable SQLite state and generates a dashboard.
        By design, this has NO mutation APIs and NO bypass controls.
        """
        wallet = self.lab.wallet()
        state = self.lab.state().name if self.lab.state() else "UNKNOWN"
        
        with self.lab.store.connection() as conn:
            trades = conn.execute("SELECT * FROM simulator_trades ORDER BY occurred_at DESC LIMIT 10").fetchall()
            events = conn.execute("SELECT * FROM audit_events ORDER BY occurred_at DESC LIMIT 10").fetchall()
            experiments = conn.execute("SELECT * FROM experiments LIMIT 5").fetchall()
            
        html = [
            "<!DOCTYPE html>",
            "<html><head><title>Trading Lab Dashboard</title>",
            "<style>body { font-family: sans-serif; margin: 2rem; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ddd; padding: 8px; } th { background-color: #f2f2f2; }</style>",
            "</head><body>",
            "<h1>🧪 Trading Lab Observability Dashboard (Read-Only)</h1>",
            
            "<h2>System Status</h2>",
            f"<p><strong>State:</strong> {state}</p>",
            f"<p><strong>Virtual Balance:</strong> ₹{wallet.balance if wallet else 'N/A'}</p>",
            f"<p><strong>Max Deployment (Risk Tier):</strong> ₹{wallet.max_deployment if wallet else 'N/A'}</p>",
            
            "<h2>Recent Trades</h2>",
            "<table><tr><th>ID</th><th>Symbol</th><th>Side</th><th>Qty</th><th>P&L</th><th>Strategy</th></tr>"
        ]
        
        for t in trades:
            side = t.get("side", "N/A")
            html.append(f"<tr><td>{t['trade_id']}</td><td>{t['symbol']}</td><td>{side}</td><td>{t['quantity']}</td><td>₹{t['pnl']}</td><td>{t['strategy_id']} v{t['strategy_version']}</td></tr>")
            
        html.append("</table>")
        
        html.append("<h2>Recent Audit Events</h2>")
        html.append("<ul>")
        for e in events:
            html.append(f"<li><strong>{e['occurred_at']} - {e['event_type']}</strong>: {e['payload_json']}</li>")
        html.append("</ul>")
        
        html.append("</body></html>")
        
        return "\n".join(html)
