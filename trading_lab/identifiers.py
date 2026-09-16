from __future__ import annotations

from uuid import uuid4


def new_strategy_id() -> str:
    """Return an immutable identifier; versions are separate integer values."""
    return f"strategy_{uuid4()}"


def new_experiment_id() -> str:
    """Return an immutable identifier for an experiment registry record."""
    return f"experiment_{uuid4()}"
