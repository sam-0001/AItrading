from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol

from .domain import SystemState
from .services import LabService
from .store import SqliteStore

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send_email(self, subject: str, body: str) -> None:
        ...


class MockEmailSender:
    def __init__(self):
        self.sent_emails = []

    def send_email(self, subject: str, body: str) -> None:
        logger.info(f"Mock sending email: {subject}")
        self.sent_emails.append({"subject": subject, "body": body})


class DailyReporter:
    def __init__(self, lab: LabService, email_client: EmailSender):
        self.lab = lab
        self.email = email_client

    def generate_daily_report(self) -> str:
        wallet = self.lab.wallet()
        if not wallet:
            return "Lab not initialized."

        with self.lab.store.connection() as conn:
            trades = conn.execute("SELECT * FROM simulator_trades").fetchall()
            events = conn.execute("SELECT * FROM audit_events WHERE event_type='AI_RESEARCH_NOTE'").fetchall()

        total_trades = len(trades)
        winners = [t for t in trades if Decimal(t["pnl"]) > 0]
        losers = [t for t in trades if Decimal(t["pnl"]) <= 0]
        
        win_rate = len(winners) / total_trades if total_trades else 0.0
        
        net_pnl = sum((Decimal(t["pnl"]) for t in trades), Decimal("0.00"))
        total_fees = sum((Decimal(t["fees"]) for t in trades), Decimal("0.00"))
        
        # Simplified report formatting
        report = []
        report.append("=== DAILY RESEARCH REPORT ===")
        report.append(f"Ending Balance: ₹{wallet.balance}")
        report.append(f"Max Deployment: ₹{wallet.max_deployment}")
        report.append(f"Net P&L: ₹{net_pnl}")
        
        report.append(f"Total Trades: {total_trades}")
        report.append(f"Win Rate: {win_rate:.2%}")
        report.append(f"Fees Paid: ₹{total_fees}")
        
        report.append("--- Trade-by-trade ---")
        for t in trades[-5:]: # Limit to last 5 for brevity
            report.append(f"Trade {t['trade_id']}: {t['side'] if 'side' in t.keys() else 'Trade'} {t['quantity']} {t['symbol']} | P&L: ₹{t['pnl']} | Strat: {t['strategy_id']}v{t['strategy_version']}")
            
        report.append("--- Research Notes ---")
        for e in events[-3:]:
            import json
            payload = json.loads(e["payload_json"])
            report.append(f"- {payload.get('notes', '')}")

        return "\n".join(report)

    def generate_death_report(self) -> str:
        wallet = self.lab.wallet()
        with self.lab.store.connection() as conn:
            trades = conn.execute("SELECT * FROM simulator_trades ORDER BY occurred_at DESC").fetchall()
            
        report = []
        report.append("!!! DEATH REPORT !!!")
        report.append(f"Final Balance: ₹{wallet.balance if wallet else 'N/A'}")
        report.append(f"The simulated lab has reached ₹0 or below and is permanently DEAD.")
        report.append("Timeline of recent losses:")
        
        for t in trades[:10]:
            if Decimal(t["pnl"]) < 0:
                report.append(f"Loss of ₹{t['pnl']} by {t['strategy_id']}v{t['strategy_version']} on {t['symbol']}")
                
        return "\n".join(report)

    def send_reports(self) -> None:
        if self.lab.state() == SystemState.DEAD:
            report = self.generate_death_report()
            self.email.send_email("ALERT: Lab Dead", report)
        else:
            report = self.generate_daily_report()
            self.email.send_email("Daily Research Report", report)
