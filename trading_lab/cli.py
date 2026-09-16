from __future__ import annotations

import argparse
from dataclasses import asdict
from decimal import Decimal

from .config import Settings
from .logging import configure_logging
from .services import LabService
from .store import SqliteStore


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Trading Lab Phase 1")
    parser.add_argument("command", choices=["init", "status", "test-loss"])
    args = parser.parse_args()
    settings = Settings.from_environment()
    configure_logging(settings.log_level)
    lab = LabService(SqliteStore(settings.database_path))
    if args.command == "init":
        lab.initialize()
    elif args.command == "test-loss":
        lab.record_accounting_entry(Decimal("-1000.00"), "manual-safety-test", "Phase 1 terminal-state demonstration")
    print({"state": lab.state().value, "wallet": {key: str(value) for key, value in asdict(lab.wallet()).items()}})


if __name__ == "__main__":
    main()
