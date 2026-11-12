
import pytest

from src.agents.investigation_state import (
    create_investigation_state,
    update_investigation_state,
    record_tool_execution,
)


def test_investigation_state_initialization():
    alert = {"alert_type": "BRUTE_FORCE"}

    state = create_investigation_state(alert)

    assert state["status"] == "initialized"
    assert state["current_step"] == "start"
    assert state["tool_calls_used"] == 0
    assert state["max_tool_calls"] == 1
    assert state["audit_log"] == []
    assert state["tool_executions"] == []
    assert state["investigation_id"]


def test_investigation_state_transition():
    state = create_investigation_state(
        {"alert_type": "BRUTE_FORCE"}
    )

    update_investigation_state(
        state, "selecting_tool", "tool_selection"
    )

    assert state["status"] == "selecting_tool"
    assert state["current_step"] == "tool_selection"
    assert len(state["audit_log"]) == 1
    assert state["audit_log"][0]["previous_status"] == "initialized"
    assert state["audit_log"][0]["new_status"] == "selecting_tool"


def test_invalid_investigation_status_rejected():
    state = create_investigation_state(
        {"alert_type": "BRUTE_FORCE"}
    )

    with pytest.raises(ValueError):
        update_investigation_state(
            state, "unknown_status", "invalid_step"
        )


def test_tool_execution_recording():
    state = create_investigation_state(
        {"alert_type": "BRUTE_FORCE"}
    )

    update_investigation_state(
        state, "executing_tool", "tool_execution"
    )

    execution = {
        "tool_name": "lookup_login_activity",
        "parameters": {"source_ip": "198.51.100.50"},
        "result": {"count": 5},
        "status": "success",
    }

    record_tool_execution(state, execution)

    assert state["tool_calls_used"] == 1
    assert len(state["tool_executions"]) == 1
    assert len(state["audit_log"]) == 2
    assert state["tool_executions"][0]["tool_name"] == (
        "lookup_login_activity"
    )


def test_tool_execution_limit_enforced():
    state = create_investigation_state(
        {"alert_type": "BRUTE_FORCE"}
    )

    update_investigation_state(
        state, "executing_tool", "tool_execution"
    )

    execution = {
        "tool_name": "lookup_login_activity",
        "parameters": {"source_ip": "198.51.100.50"},
        "result": {"count": 5},
        "status": "success",
    }

    record_tool_execution(state, execution)

    with pytest.raises(RuntimeError):
        record_tool_execution(state, execution)

    assert state["tool_calls_used"] == 1
    assert len(state["tool_executions"]) == 1


def test_completed_investigation_cannot_be_updated():
    state = create_investigation_state(
        {"alert_type": "BRUTE_FORCE"}
    )

    update_investigation_state(
        state, "completed", "investigation_complete"
    )

    assert state["completed_at"] is not None

    with pytest.raises(ValueError):
        update_investigation_state(
            state, "executing_tool", "tool_execution"
        )