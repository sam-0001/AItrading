from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "Settings":
        raw_path = os.environ.get("TRADING_LAB_DATABASE_PATH", "data/trading_lab.sqlite3")
        return cls(Path(raw_path), os.environ.get("TRADING_LAB_LOG_LEVEL", "INFO").upper())
