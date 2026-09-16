from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal

from .domain import DomainError, WalletSnapshot
from .services import LabService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RiskTier:
    tier_level: int
    min_wallet_balance: Decimal
    max_wallet_balance: Decimal | None
    max_deployment: Decimal


class DynamicCapitalManager:
    """Manages the evaluation and application of Risk Tiers to the LabService."""

    # Default tiers as specified in Phase 7 logic
    TIERS = [
        RiskTier(1, Decimal("1000.00"), Decimal("1499.99"), Decimal("500.00")),
        RiskTier(2, Decimal("1500.00"), Decimal("2499.99"), Decimal("750.00")),
        RiskTier(3, Decimal("2500.00"), Decimal("4999.99"), Decimal("1250.00")),
        RiskTier(4, Decimal("5000.00"), None, Decimal("2000.00")),
    ]

    def __init__(self, lab: LabService, min_trades_required: int = 10, min_win_rate: float = 0.4):
        self.lab = lab
        self.min_trades_required = min_trades_required
        self.min_win_rate = min_win_rate

    def evaluate_and_apply_tier(self) -> WalletSnapshot:
        """
        Evaluates current wallet balance and trading performance, 
        demoting or promoting the deployment tier dynamically.
        """
        wallet = self.lab.wallet()
        
        # Determine the target tier based strictly on wallet bounds
        target_tier = self._find_tier_for_balance(wallet.balance)

        # Check performance rules before allowing an upgrade. 
        # Demotions are automatic if balance drops. Promotions need justification.
        current_max = wallet.max_deployment
        is_promotion = target_tier.max_deployment > current_max

        if is_promotion:
            if not self._check_promotion_requirements():
                logger.info("Promotion to tier %d denied due to missing performance requirements", target_tier.tier_level)
                return wallet

        if target_tier.max_deployment != current_max:
            logger.info("Updating tier to level %d. New Max Deployment: %s", target_tier.tier_level, target_tier.max_deployment)
            return self.lab.update_max_deployment(
                target_tier.max_deployment, 
                f"Dynamic capital transition to Tier {target_tier.tier_level}"
            )
            
        return wallet

    def _find_tier_for_balance(self, balance: Decimal) -> RiskTier:
        for tier in self.TIERS:
            if tier.min_wallet_balance <= balance:
                if tier.max_wallet_balance is None or balance <= tier.max_wallet_balance:
                    return tier
        
        # If below tier 1 but not DEAD, default to tier 1 max deployment bounds to allow recovery.
        return self.TIERS[0]

    def _check_promotion_requirements(self) -> bool:
        """Checks trades count and win rate against immutable trades."""
        with self.lab.store.connection() as conn:
            trades = conn.execute("SELECT pnl FROM simulator_trades").fetchall()
            
        total_trades = len(trades)
        if total_trades < self.min_trades_required:
            return False
            
        wins = sum(1 for t in trades if Decimal(t["pnl"]) > 0)
        win_rate = wins / total_trades
        
        if win_rate < self.min_win_rate:
            return False
            
        return True
