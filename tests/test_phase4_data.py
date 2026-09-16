from datetime import datetime, timezone
import pytest
from decimal import Decimal

from trading_lab.data import HistoricalDataPipeline, Bar, DataValidationError

def test_ingest_csv_success():
    pipeline = HistoricalDataPipeline()
    csv_data = [
        "timestamp_iso,open,high,low,close,volume",
        "2026-09-01T10:00:00+00:00,100,105,99,104,1000",
        "2026-09-02T10:00:00+00:00,104,106,103,105,1200",
    ]
    bars = pipeline.ingest_csv("RELIANCE", csv_data)
    assert len(bars) == 2
    assert bars[0].close == Decimal("104")
    assert bars[1].volume == 1200

def test_ingest_duplicate_rejection():
    pipeline = HistoricalDataPipeline()
    csv_data = [
        "timestamp_iso,open,high,low,close,volume",
        "2026-09-01T10:00:00+00:00,100,105,99,104,1000",
        "2026-09-01T10:00:00+00:00,104,106,103,105,1200",  # duplicate
    ]
    with pytest.raises(DataValidationError, match="Duplicate timestamp"):
        pipeline.ingest_csv("RELIANCE", csv_data)

def test_partitioning_prevents_lookahead():
    pipeline = HistoricalDataPipeline()
    
    # 3 bars, one per day
    dt1 = datetime(2026, 9, 1, 10, tzinfo=timezone.utc)
    dt2 = datetime(2026, 9, 2, 10, tzinfo=timezone.utc)
    dt3 = datetime(2026, 9, 3, 10, tzinfo=timezone.utc)
    
    bars = [
        Bar("REL", dt1, Decimal("10"), Decimal("10"), Decimal("10"), Decimal("10"), 100),
        Bar("REL", dt2, Decimal("11"), Decimal("11"), Decimal("11"), Decimal("11"), 100),
        Bar("REL", dt3, Decimal("12"), Decimal("12"), Decimal("12"), Decimal("12"), 100),
    ]
    
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 2, 23, 59, tzinfo=timezone.utc)
    
    partition = pipeline.create_partition("REL", bars, start, end)
    
    assert len(partition.bars) == 2
    assert partition.bars[-1].timestamp == dt2
    # dt3 is strictly excluded to prevent lookahead
