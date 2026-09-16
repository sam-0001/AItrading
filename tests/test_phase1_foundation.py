from __future__ import annotations

from decimal import Decimal

import pytest

from trading_lab.domain import (INITIAL_MAX_DEPLOYMENT, INITIAL_VIRTUAL_BALANCE,
                                ImmutableRecordError, InvalidStateTransition,
                                SystemState, TerminalExperimentError)
from trading_lab.identifiers import new_experiment_id, new_strategy_id
from trading_lab.services import LabService
from trading_lab.store import SqliteStore


@pytest.fixture
def lab(tmp_path):
    return LabService(SqliteStore(tmp_path / "lab.sqlite3"))


def test_initial_wallet_and_deployment_are_exact(lab):
    assert lab.wallet().balance == INITIAL_VIRTUAL_BALANCE
    assert lab.wallet().max_deployment == INITIAL_MAX_DEPLOYMENT
    assert lab.state() is SystemState.INITIALIZING


def test_invalid_state_transition_is_rejected(lab):
    with pytest.raises(InvalidStateTransition):
        lab.transition(SystemState.MARKET_OPEN)


def test_terminal_death_persists_across_restart_and_blocks_mutation(tmp_path):
    path = tmp_path / "lab.sqlite3"
    first_process = LabService(SqliteStore(path))
    first_process.record_accounting_entry(Decimal("-1000.00"), "loss-001", "deterministic test loss")
    assert first_process.wallet().balance == Decimal("0.00")
    assert first_process.state() is SystemState.DEAD

    restarted_process = LabService(SqliteStore(path))
    assert restarted_process.state() is SystemState.DEAD
    with pytest.raises(TerminalExperimentError):
        restarted_process.transition(SystemState.INITIALIZING)
    with pytest.raises(TerminalExperimentError):
        restarted_process.record_accounting_entry(Decimal("1.00"), "refill", "must never refill DEAD")
    with pytest.raises(TerminalExperimentError):
        restarted_process.transition(SystemState.MARKET_OPEN, actor="untrusted-ai")


def test_wallet_changes_only_through_accounting_service_and_is_audited(lab):
    before = lab.wallet()
    after = lab.record_accounting_entry(Decimal("-25.50"), "loss-002", "test loss")
    assert before.balance == Decimal("1000.00")
    assert after.balance == Decimal("974.50")
    assert [event.event_type for event in lab.store.events()] == ["LAB_INITIALIZED", "ACCOUNTING_ENTRY"]


def test_audit_history_is_append_only(lab):
    event = lab.store.append_event("TEST_EVENT", {"result": "recorded"})
    with pytest.raises(ImmutableRecordError):
        lab.store.update_event_for_test_only(event.event_id)


def test_strategy_and_experiment_identifiers_are_distinct_and_versionable(lab):
    strategy_id = new_strategy_id()
    experiment_id = new_experiment_id()
    assert strategy_id.startswith("strategy_")
    assert experiment_id.startswith("experiment_")
    lab.store.create_immutable_strategy_version(strategy_id, 1, {"hypothesis": "not executable in phase 1"})
    lab.store.create_immutable_experiment(experiment_id, {"status": "registered"})
