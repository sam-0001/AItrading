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
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>AI Trading Lab - Dashboard</title>",
            "    <script src='https://cdn.tailwindcss.com'></script>",
            "    <style>",
            "        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');",
            "        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }",
            "        .bento-card {",
            "            background: #1e293b;",
            "            border: 1px solid #334155;",
            "            border-radius: 1.5rem;",
            "            padding: 1.5rem;",
            "            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);",
            "            transition: transform 0.2s ease, box-shadow 0.2s ease;",
            "        }",
            "        .bento-card:hover {",
            "            transform: translateY(-2px);",
            "            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);",
            "        }",
            "        .badge {",
            "            padding: 0.25rem 0.75rem;",
            "            border-radius: 9999px;",
            "            font-size: 0.75rem;",
            "            font-weight: 600;",
            "            text-transform: uppercase;",
            "            letter-spacing: 0.05em;",
            "        }",
            "        .badge-running { background: #047857; color: #a7f3d0; }",
            "        .badge-closed { background: #b91c1c; color: #fecaca; }",
            "        .badge-research { background: #4338ca; color: #c7d2fe; }",
            "        .badge-buy { background: #166534; color: #bbf7d0; }",
            "        .badge-sell { background: #991b1b; color: #fecaca; }",
            "        /* Custom scrollbar for tables */",
            "        .table-container::-webkit-scrollbar { height: 8px; }",
            "        .table-container::-webkit-scrollbar-track { background: #0f172a; border-radius: 4px; }",
            "        .table-container::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }",
            "    </style>",
            "</head>",
            "<body class='min-h-screen p-4 md:p-8'>",
            "    <div class='max-w-7xl mx-auto'>",
            "        <!-- Header -->",
            "        <header class='mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4'>",
            "            <div>",
            "                <h1 class='text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400'>AI Trading Lab</h1>",
            "                <p class='text-slate-400 text-sm mt-1'>Autonomous Quantitative Research Environment</p>",
            "            </div>",
            f"            <div class='badge {'badge-running' if state == 'MARKET_OPEN' else 'badge-research' if state == 'RESEARCH' else 'badge-closed'} text-sm px-4 py-1.5'>",
            f"                System State: {state}",
            "            </div>",
            "        </header>",
            "",
            "        <!-- Bento Grid Layout -->",
            "        <div class='grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-min'>",
            "",
            "            <!-- KPI Cards -->",
            "            <div class='bento-card col-span-1 md:col-span-1 flex flex-col justify-center'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-2'>Virtual Balance</h3>",
            f"                <div class='text-4xl font-bold text-white'>₹{wallet.balance if wallet else '0.00'}</div>",
            "            </div>",
            "            <div class='bento-card col-span-1 md:col-span-1 flex flex-col justify-center'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-2'>Risk Tier</h3>",
            f"                <div class='text-4xl font-bold text-emerald-400'>₹{wallet.max_deployment if wallet else '0.00'}</div>",
            "                <p class='text-xs text-slate-500 mt-1'>Max deployment per trade</p>",
            "            </div>",
            "            <div class='bento-card col-span-1 md:col-span-2 lg:col-span-2'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4'>Recent Experiments</h3>",
            "                <div class='flex gap-2 flex-wrap'>"
        ]
        
        for exp in experiments:
            html.append(f"<span class='px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg text-sm font-mono text-blue-300'>{exp['experiment_id']}</span>")
        if not experiments:
            html.append("<span class='text-slate-500 text-sm italic'>No experiments yet</span>")
            
        html.extend([
            "                </div>",
            "            </div>",
            "",
            "            <!-- Trades Table (Spans 2 columns on large) -->",
            "            <div class='bento-card col-span-1 md:col-span-3 lg:col-span-2 lg:row-span-2 flex flex-col'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4 flex items-center justify-between'>",
            "                    Recent Executions",
            f"                    <span class='text-xs bg-slate-800 px-2 py-1 rounded text-slate-300'>{len(trades)} Trades</span>",
            "                </h3>",
            "                <div class='overflow-x-auto table-container flex-grow'>",
            "                    <table class='w-full text-left text-sm whitespace-nowrap'>",
            "                        <thead>",
            "                            <tr class='border-b border-slate-700 text-slate-400'>",
            "                                <th class='pb-3 font-medium px-2'>Symbol</th>",
            "                                <th class='pb-3 font-medium px-2'>Side</th>",
            "                                <th class='pb-3 font-medium text-right px-2'>Qty</th>",
            "                                <th class='pb-3 font-medium text-right px-2'>P&L</th>",
            "                            </tr>",
            "                        </thead>",
            "                        <tbody class='divide-y divide-slate-700/50'>"
        ])
        
        for t in trades:
            side = dict(t).get("side", "N/A") if hasattr(t, "keys") else t["side"]
            side_badge = "badge-buy" if side == "BUY" else "badge-sell" if side == "SELL" else "bg-slate-700 text-slate-300"
            pnl_val = float(dict(t).get('pnl', 0) if hasattr(t, "keys") else t["pnl"])
            pnl_color = "text-emerald-400" if pnl_val > 0 else "text-red-400" if pnl_val < 0 else "text-slate-300"
            html.append(f"                            <tr class='hover:bg-slate-800/50 transition-colors'>")
            html.append(f"                                <td class='py-3 px-2 font-medium'>{t['symbol']}</td>")
            html.append(f"                                <td class='py-3 px-2'><span class='badge {side_badge} text-[10px]'>{side}</span></td>")
            html.append(f"                                <td class='py-3 px-2 text-right font-mono text-slate-300'>{t['quantity']}</td>")
            html.append(f"                                <td class='py-3 px-2 text-right font-mono {pnl_color}'>{'+' if pnl_val > 0 else ''}₹{t['pnl']}</td>")
            html.append(f"                            </tr>")
            
        if not trades:
            html.append("<tr><td colspan='4' class='py-8 text-center text-slate-500 italic'>No trades executed yet</td></tr>")
            
        html.extend([
            "                        </tbody>",
            "                    </table>",
            "                </div>",
            "            </div>",
            "",
            "            <!-- Audit Log (Spans 2 columns on large) -->",
            "            <div class='bento-card col-span-1 md:col-span-3 lg:col-span-2 lg:row-span-2 flex flex-col'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4 flex items-center justify-between'>",
            "                    System Audit Log",
            f"                    <span class='text-xs bg-slate-800 px-2 py-1 rounded text-slate-300'>Last {len(events)} Events</span>",
            "                </h3>",
            "                <div class='flex-grow overflow-y-auto pr-2 space-y-3 table-container' style='max-height: 400px;'>",
        ])
        
        for e in events:
            evt_type = dict(e).get('event_type', 'UNKNOWN') if hasattr(e, "keys") else e["event_type"]
            html.append(f"                    <div class='p-3 rounded-xl bg-slate-900/50 border border-slate-800'>")
            html.append(f"                        <div class='flex justify-between items-start mb-1'>")
            html.append(f"                            <span class='text-xs font-bold text-blue-400'>{evt_type}</span>")
            html.append(f"                            <span class='text-[10px] text-slate-500 font-mono'>{e['occurred_at'][:19]}</span>")
            html.append(f"                        </div>")
            html.append(f"                        <p class='text-xs text-slate-300 font-mono break-words leading-relaxed'>{e['payload_json']}</p>")
            html.append(f"                    </div>")
            
        if not events:
            html.append("<div class='py-8 text-center text-slate-500 italic'>No audit events recorded</div>")

        html.extend([
            "                </div>",
            "            </div>",
            "",
            "        </div>",
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
