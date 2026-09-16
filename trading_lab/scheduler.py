import time
import logging
from datetime import datetime, timezone

from .domain import SystemState
from .services import LabService
from .clock import MarketClock
from .reporting import DailyReporter

logger = logging.getLogger(__name__)


class LabScheduler:
    """Simulates a VPS cron or continuous loop for Phase 9."""

    def __init__(self, lab: LabService, clock: MarketClock, reporter: DailyReporter):
        self.lab = lab
        self.clock = clock
        self.reporter = reporter
        self.running = False

    def start(self):
        self.running = True
        logger.info("Starting VPS Scheduler Loop...")
        while self.running:
            self._tick()
            # Simulated sleep for testability
            break

    def _tick(self):
        try:
            current_time = datetime.now(timezone.utc)
            expected_state = self.clock.get_market_state(current_time)
            current_state = self.lab.state()

            # Ensure DEAD is absolute terminal
            if current_state == SystemState.DEAD:
                logger.warning("System is DEAD. Halting scheduler.")
                self.running = False
                return

            if current_state != expected_state and expected_state != SystemState.ERROR_SAFE:
                logger.info(f"Transitioning from {current_state} to {expected_state}")
                
                # Check if we need to go through intermediate states
                if current_state in (SystemState.INITIALIZING, SystemState.RESEARCH) and expected_state == SystemState.MARKET_OPEN:
                    self.lab.transition(SystemState.PRE_MARKET)
                    
                self.lab.transition(expected_state)

                if expected_state == SystemState.MARKET_CLOSED:
                    self._run_end_of_day_jobs()
                    
        except Exception as e:
            logger.error("Scheduler encountered an error: %s", e)
            self.lab.transition(SystemState.ERROR_SAFE)

    def _run_end_of_day_jobs(self):
        logger.info("Running End-of-Day jobs...")
        self.reporter.send_reports()
        
        # Transition to research
        self.lab.transition(SystemState.RESEARCH)
        logger.info("Running AI Research Loop...")
        # (In a real system, invoke ResearchLoop here)
