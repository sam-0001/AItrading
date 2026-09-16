import logging
import threading
import time
from pathlib import Path

from trading_lab.services import LabService
from trading_lab.store import SqliteStore
from trading_lab.scheduler import LabScheduler
from trading_lab.clock import MarketClock
from trading_lab.reporting import DailyReporter, MockEmailSender
from trading_lab.server import start_server

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Trading Lab...")
    db_path = Path("data/lab.db")
    db_path.parent.mkdir(exist_ok=True)
    
    store = SqliteStore(db_path)
    from trading_lab.migrations import apply_migrations
    with store.connection() as conn:
        apply_migrations(conn)
        
    lab = LabService(store)
    lab.initialize()
    
    # Start the Read-Only Dashboard Server in a background thread
    server_thread = threading.Thread(target=start_server, args=(8080,), daemon=True)
    server_thread.start()
    
    # Setup Scheduler
    clock = MarketClock()
    email_sender = MockEmailSender()
    reporter = DailyReporter(lab, email_sender)
    
    scheduler = LabScheduler(lab, clock, reporter)
    
    try:
        # Override scheduler loop to run continuously for real execution
        logger.info("Entering continuous scheduler loop...")
        scheduler.running = True
        while scheduler.running:
            scheduler._tick()
            time.sleep(60) # Tick every minute
    except KeyboardInterrupt:
        logger.info("Shutting down Trading Lab...")
        scheduler.running = False

if __name__ == "__main__":
    main()
