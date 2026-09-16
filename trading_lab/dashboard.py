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
            trades = conn.execute("SELECT * FROM simulator_trades ORDER BY occurred_at DESC").fetchall()
            events = conn.execute("SELECT * FROM audit_events ORDER BY occurred_at DESC LIMIT 50").fetchall()
            experiments = conn.execute("SELECT * FROM experiments ORDER BY created_at DESC").fetchall()
            
        import json
        
        # Prepare chart data
        trades_list = [dict(t) for t in reversed(trades)]
        cumulative_pnl = 0
        pnl_labels = []
        pnl_data = []
        for t in trades_list:
            cumulative_pnl += float(t.get('pnl', 0))
            pnl_labels.append(t.get('occurred_at', '')[:10])
            pnl_data.append(cumulative_pnl)
            
        if not pnl_data:
            pnl_labels = ["Day 1", "Day 2", "Day 3"]
            pnl_data = [0, 0, 0]

        html = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>AI Trading Lab - Dashboard</title>",
            "    <script src='https://cdn.tailwindcss.com'></script>",
            "    <script defer src='https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js'></script>",
            "    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>",
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
            "        .bento-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }",
            "        .badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }",
            "        .badge-running { background: #047857; color: #a7f3d0; }",
            "        .badge-closed { background: #b91c1c; color: #fecaca; }",
            "        .badge-research { background: #4338ca; color: #c7d2fe; }",
            "        .badge-buy { background: #166534; color: #bbf7d0; }",
            "        .badge-sell { background: #991b1b; color: #fecaca; }",
            "        .table-container::-webkit-scrollbar { height: 8px; width: 8px; }",
            "        .table-container::-webkit-scrollbar-track { background: #0f172a; border-radius: 4px; }",
            "        .table-container::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }",
            "        .nav-tab { padding: 0.75rem 1.5rem; font-weight: 500; color: #94a3b8; border-bottom: 2px solid transparent; transition: all 0.2s; cursor: pointer; }",
            "        .nav-tab:hover { color: #f8fafc; }",
            "        .nav-tab.active { color: #38bdf8; border-bottom-color: #38bdf8; }",
            "    </style>",
            "</head>",
            f"<body class='min-h-screen p-4 md:p-8' x-data=\"{{ tab: 'overview', initChart() {{ new Chart(document.getElementById('pnlChart'), {{ type: 'line', data: {{ labels: {json.dumps(pnl_labels)}, datasets: [{{ label: 'Cumulative P&L (₹)', data: {json.dumps(pnl_data)}, borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', borderWidth: 2, fill: true, tension: 0.4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#334155' }} }}, x: {{ grid: {{ display: false }} }} }} }} }}); }} }}\">",
            "    <div class='max-w-7xl mx-auto'>",
            "        <!-- Header -->",
            "        <header class='mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4'>",
            "            <div>",
            "                <h1 class='text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400'>AI Trading Lab</h1>",
            "                <p class='text-slate-400 text-sm mt-1'>Autonomous Quantitative Research Environment</p>",
            "            </div>",
            f"            <div class='badge {'badge-running' if state == 'MARKET_OPEN' else 'badge-research' if state == 'RESEARCH' else 'badge-closed'} text-sm px-4 py-1.5'>",
            f"                System State: {state}",
            "            </div>",
            "        </header>",
            "",
            "        <!-- Navigation Tabs -->",
            "        <div class='flex border-b border-slate-700 mb-8 space-x-2'>",
            "            <button @click=\"tab = 'overview'\" :class=\"{'active': tab === 'overview'}\" class='nav-tab'>Overview</button>",
            "            <button @click=\"tab = 'analytics'; $nextTick(() => { initChart() })\" :class=\"{'active': tab === 'analytics'}\" class='nav-tab'>Analytics</button>",
            "            <button @click=\"tab = 'strategies'\" :class=\"{'active': tab === 'strategies'}\" class='nav-tab'>Strategies</button>",
            "        </div>",
            "",
            "        <!-- TAB 1: OVERVIEW -->",
            "        <div x-show=\"tab === 'overview'\" class='grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-min'>",
            "            <!-- KPI Cards -->",
            "            <div class='bento-card flex flex-col justify-center'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-2'>Virtual Balance</h3>",
            f"                <div class='text-4xl font-bold text-white'>₹{wallet.balance if wallet else '0.00'}</div>",
            "            </div>",
            "            <div class='bento-card flex flex-col justify-center'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-2'>Risk Tier</h3>",
            f"                <div class='text-4xl font-bold text-emerald-400'>₹{wallet.max_deployment if wallet else '0.00'}</div>",
            "                <p class='text-xs text-slate-500 mt-1'>Max deployment per trade</p>",
            "            </div>",
            "            <div class='bento-card col-span-1 md:col-span-2 lg:col-span-2'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4'>Recent Experiments</h3>",
            "                <div class='flex gap-2 flex-wrap'>"
        ]
        
        for exp in experiments[:5]:
            html.append(f"<span class='px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg text-sm font-mono text-blue-300'>{dict(exp).get('experiment_id', 'Unknown')}</span>")
        if not experiments:
            html.append("<span class='text-slate-500 text-sm italic'>No experiments yet</span>")
            
        html.extend([
            "                </div>",
            "            </div>",
            "",
            "            <!-- Trades Table -->",
            "            <div class='bento-card col-span-1 md:col-span-3 lg:col-span-2 lg:row-span-2 flex flex-col'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4 flex items-center justify-between'>",
            "                    Recent Executions",
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
        
        for t in trades[:10]:
            side = dict(t).get("side", "N/A") if hasattr(t, "keys") else t["side"]
            side_badge = "badge-buy" if side == "BUY" else "badge-sell" if side == "SELL" else "bg-slate-700 text-slate-300"
            pnl_val = float(dict(t).get('pnl', 0) if hasattr(t, "keys") else t["pnl"])
            pnl_color = "text-emerald-400" if pnl_val > 0 else "text-red-400" if pnl_val < 0 else "text-slate-300"
            html.append(f"                            <tr class='hover:bg-slate-800/50 transition-colors'>")
            html.append(f"                                <td class='py-3 px-2 font-medium'>{dict(t).get('symbol', '')}</td>")
            html.append(f"                                <td class='py-3 px-2'><span class='badge {side_badge} text-[10px]'>{side}</span></td>")
            html.append(f"                                <td class='py-3 px-2 text-right font-mono text-slate-300'>{dict(t).get('quantity', 0)}</td>")
            html.append(f"                                <td class='py-3 px-2 text-right font-mono {pnl_color}'>{'+' if pnl_val > 0 else ''}₹{pnl_val}</td>")
            html.append(f"                            </tr>")
            
        if not trades:
            html.append("<tr><td colspan='4' class='py-8 text-center text-slate-500 italic'>No trades executed yet</td></tr>")
            
        html.extend([
            "                        </tbody>",
            "                    </table>",
            "                </div>",
            "            </div>",
            "",
            "            <!-- Audit Log -->",
            "            <div class='bento-card col-span-1 md:col-span-3 lg:col-span-2 lg:row-span-2 flex flex-col'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4 flex items-center justify-between'>",
            "                    System Audit Log",
            "                </h3>",
            "                <div class='flex-grow overflow-y-auto pr-2 space-y-3 table-container' style='max-height: 400px;'>",
        ])
        
        for e in events[:15]:
            evt_type = dict(e).get('event_type', 'UNKNOWN') if hasattr(e, "keys") else e["event_type"]
            payload = dict(e).get('payload_json', '') if hasattr(e, "keys") else e["payload_json"]
            occurred_at = dict(e).get('occurred_at', '') if hasattr(e, "keys") else e["occurred_at"]
            html.append(f"                    <div class='p-3 rounded-xl bg-slate-900/50 border border-slate-800'>")
            html.append(f"                        <div class='flex justify-between items-start mb-1'>")
            html.append(f"                            <span class='text-xs font-bold text-blue-400'>{evt_type}</span>")
            html.append(f"                            <span class='text-[10px] text-slate-500 font-mono'>{occurred_at[:19]}</span>")
            html.append(f"                        </div>")
            html.append(f"                        <p class='text-xs text-slate-300 font-mono break-words leading-relaxed'>{payload}</p>")
            html.append(f"                    </div>")
            
        if not events:
            html.append("<div class='py-8 text-center text-slate-500 italic'>No audit events recorded</div>")

        html.extend([
            "                </div>",
            "            </div>",
            "        </div>", # End Overview Tab
            
            "        <!-- TAB 2: ANALYTICS -->",
            "        <div x-show=\"tab === 'analytics'\" style='display: none;' class='space-y-6'>",
            "            <div class='bento-card'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4'>Cumulative Profit & Loss</h3>",
            "                <div class='w-full h-80'>",
            "                    <canvas id='pnlChart'></canvas>",
            "                </div>",
            "            </div>",
            "            <div class='grid grid-cols-1 md:grid-cols-2 gap-6'>",
            "                <div class='bento-card'>",
            "                    <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4'>Trade Statistics</h3>",
            f"                    <div class='space-y-4 text-sm'>",
            f"                        <div class='flex justify-between pb-2 border-b border-slate-700'><span class='text-slate-400'>Total Executions</span><span class='font-mono text-white'>{len(trades)}</span></div>",
            f"                        <div class='flex justify-between pb-2 border-b border-slate-700'><span class='text-slate-400'>Gross P&L</span><span class='font-mono {'text-emerald-400' if cumulative_pnl >= 0 else 'text-red-400'}'>₹{cumulative_pnl:.2f}</span></div>",
            f"                    </div>",
            "                </div>",
            "            </div>",
            "        </div>", # End Analytics Tab
            
            "        <!-- TAB 3: STRATEGIES -->",
            "        <div x-show=\"tab === 'strategies'\" style='display: none;' class='space-y-6'>",
            "            <div class='bento-card'>",
            "                <h3 class='text-slate-400 text-sm font-medium uppercase tracking-wider mb-4'>AI Research Experiments</h3>",
            "                <div class='overflow-x-auto table-container'>",
            "                    <table class='w-full text-left text-sm whitespace-nowrap'>",
            "                        <thead>",
            "                            <tr class='border-b border-slate-700 text-slate-400'>",
            "                                <th class='pb-3 font-medium px-2'>Experiment ID</th>",
            "                                <th class='pb-3 font-medium px-2'>Strategy Spec</th>",
            "                                <th class='pb-3 font-medium px-2'>Created At</th>",
            "                            </tr>",
            "                        </thead>",
            "                        <tbody class='divide-y divide-slate-700/50'>"
        ])
        
        for exp in experiments:
            exp_dict = dict(exp)
            html.append(f"                            <tr class='hover:bg-slate-800/50 transition-colors'>")
            html.append(f"                                <td class='py-3 px-2 font-mono text-blue-400'>{exp_dict.get('experiment_id', '')}</td>")
            html.append(f"                                <td class='py-3 px-2 font-mono text-slate-300 text-xs whitespace-pre-wrap max-w-lg break-words overflow-hidden'>{exp_dict.get('strategy_spec_json', '{}')[:100]}...</td>")
            html.append(f"                                <td class='py-3 px-2 font-mono text-slate-500'>{exp_dict.get('created_at', '')[:19]}</td>")
            html.append(f"                            </tr>")
            
        if not experiments:
            html.append("<tr><td colspan='3' class='py-8 text-center text-slate-500 italic'>No AI experiments found</td></tr>")
            
        html.extend([
            "                        </tbody>",
            "                    </table>",
            "                </div>",
            "            </div>",
            "        </div>", # End Strategies Tab
            "",
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
