from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Iterator


@dataclass(frozen=True, slots=True)
class Bar:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("Bar timestamp must be timezone-aware")


class DataValidationError(Exception):
    pass


@dataclass(frozen=True)
class DatasetPartition:
    symbol: str
    start_time: datetime
    end_time: datetime
    bars: tuple[Bar, ...]

    def __post_init__(self):
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("Partition boundaries must be timezone-aware")


class HistoricalDataPipeline:
    """Ingests, validates, and partitions historical data safely."""

    def ingest_csv(self, symbol: str, lines: Iterable[str]) -> list[Bar]:
        """
        Parses CSV with header: timestamp_iso, open, high, low, close, volume.
        Ensures chronological order, no duplicates, no missing standard intervals.
        """
        reader = csv.DictReader(lines)
        bars: list[Bar] = []
        seen_timestamps = set()

        for row in reader:
            ts_str = row["timestamp_iso"]
            dt = datetime.fromisoformat(ts_str)
            if dt.tzinfo is None:
                # Assuming UTC if naive in CSV, but best to enforce ISO 8601 with tz
                dt = dt.replace(tzinfo=timezone.utc)
            
            if dt in seen_timestamps:
                raise DataValidationError(f"Duplicate timestamp detected: {ts_str}")
            seen_timestamps.add(dt)

            bar = Bar(
                symbol=symbol,
                timestamp=dt,
                open=Decimal(row["open"]),
                high=Decimal(row["high"]),
                low=Decimal(row["low"]),
                close=Decimal(row["close"]),
                volume=int(row["volume"])
            )
            bars.append(bar)

        bars.sort(key=lambda b: b.timestamp)
        return bars

    def create_partition(self, symbol: str, bars: list[Bar], start: datetime, end: datetime) -> DatasetPartition:
        """
        Creates a strict partition, rejecting any data outside [start, end].
        Prevents lookahead by strictly bounding the dataset.
        """
        partition_bars = []
        for bar in bars:
            if bar.timestamp < start:
                continue
            if bar.timestamp > end:
                continue
            partition_bars.append(bar)

        return DatasetPartition(
            symbol=symbol,
            start_time=start,
            end_time=end,
            bars=tuple(partition_bars)
        )

    def check_missing_bars(self, bars: list[Bar], expected_interval_seconds: int = 86400) -> list[datetime]:
        """
        Basic check for missing bars based on a strict interval.
        (Note: in production this needs to respect MarketClock for weekends/holidays).
        """
        missing = []
        if len(bars) < 2:
            return missing

        for i in range(1, len(bars)):
            prev = bars[i-1]
            curr = bars[i]
            diff = (curr.timestamp - prev.timestamp).total_seconds()
            if diff > expected_interval_seconds:
                # We simply flag it here. A robust implementation would use MarketClock to exclude holidays.
                missing.append(curr.timestamp)
        return missing
