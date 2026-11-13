from unittest.mock import patch

from src.agents.agentic_workflow import run_agentic_investigation


def test_agentic_workflow_executes_approved_tool():
    """Verify the workflow executes the selected investigation tool."""

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    selection = {
        "tool_name": "lookup_login_activity",
        "parameters": {
            "source_ip": "198.51.100.50",
        },
    }

    # execution = {
    #     "tool_name": "lookup_login_activity",
    #     "status": "success",
    #     "result": {
    #         "source_ip": "198.51.100.50",
    #         "event_count": 5,
    #         "matching_events": [],
    #     },
    # }

    execution = {
        "tool_name": "lookup_login_activity",
        "parameters": {
            "source_ip": "198.51.100.50",
        },
        "status": "success",
        "result": {
            "source_ip": "198.51.100.50",
            "event_count": 5,
            "matching_events": [],
        },
    }

    with patch(
        "src.agents.agentic_workflow.select_investigation_tool",
        return_value=selection,
    ), patch(
        "src.agents.agentic_workflow.execute_tool",
        return_value=execution,
    ) as mock_executor:

        result = run_agentic_investigation(alert)

    assert result["status"] == "completed"
    assert result["selection"] == selection
    assert result["tool_execution"] == execution

    mock_executor.assert_called_once_with(
        tool_name="lookup_login_activity",
        parameters={"source_ip": "198.51.100.50"},
    )


def test_agentic_workflow_handles_no_tool_selected():
    """Verify no tool executes when AI selects none."""

    alert = {
        "alert_type": "INFORMATIONAL",
        "severity": "low",
        "description": "No additional investigation required",
    }

    selection = {
        "tool_name": None,
        "parameters": {},
    }

    with patch(
        "src.agents.agentic_workflow.select_investigation_tool",
        return_value=selection,
    ), patch(
        "src.agents.agentic_workflow.execute_tool",
    ) as mock_executor:

        result = run_agentic_investigation(alert)

    assert result["status"] == "no_tool_selected"
    assert result["selection"] == selection
    assert result["tool_execution"] is None

    mock_executor.assert_not_called()


def test_agentic_workflow_records_complete_audit_trail():
    """Verify the workflow records a complete investigation."""

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    selection = {
        "tool_name": "lookup_login_activity",
        "parameters": {
            "source_ip": "198.51.100.50",
        },
    }

    execution = {
        "tool_name": "lookup_login_activity",
        "parameters": {
            "source_ip": "198.51.100.50",
        },
        "status": "success",
        "result": {
            "source_ip": "198.51.100.50",
            "event_count": 5,
            "matching_events": [],
        },
    }

    with patch(
        "src.agents.agentic_workflow.select_investigation_tool",
        return_value=selection,
    ), patch(
        "src.agents.agentic_workflow.execute_tool",
        return_value=execution,
    ) as mock_executor:

        result = run_agentic_investigation(alert)

    state = result["investigation_state"]

    assert result["status"] == "completed"
    assert state["status"] == "completed"
    assert state["tool_calls_used"] == 1
    assert len(state["tool_executions"]) == 1
    assert state["completed_at"] is not None

    # assert len(state["audit_log"]) == 4
    assert len(state["audit_log"]) == 5
    assert state["tool_attempts"] == 1
    assert state["audit_log"][2]["event"] == "tool_attempt"

    assert [
        entry.get("new_status")
        for entry in state["audit_log"]
        if "new_status" in entry
    ] == [
        "selecting_tool",
        "executing_tool",
        "completed",
    ]

    assert state["audit_log"][3]["event"] == "tool_execution"

    mock_executor.assert_called_once_with(
        tool_name="lookup_login_activity",
        parameters={"source_ip": "198.51.100.50"},
    )


def test_agentic_workflow_handles_tool_execution_failure():
    """Verify tool failures produce an auditable failed state."""

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    selection = {
        "tool_name": "lookup_login_activity",
        "parameters": {
            "source_ip": "198.51.100.50",
        },
    }

    with patch(
        "src.agents.agentic_workflow.select_investigation_tool",
        return_value=selection,
    ), patch(
        "src.agents.agentic_workflow.execute_tool",
        side_effect=RuntimeError("Simulated evidence lookup failure"),
    ) as mock_executor:

        result = run_agentic_investigation(alert)

    state = result["investigation_state"]

    assert result["status"] == "failed"
    assert state["status"] == "failed"
    assert state["completed_at"] is not None
    assert state["investigation_id"]

    assert result["tool_execution"] is None
    assert result["error"] == "Simulated evidence lookup failure"

    assert state["tool_calls_used"] == 0
    assert len(state["tool_executions"]) == 0

    assert any(
        entry.get("event") == "investigation_error"
        and entry.get("error_type") == "RuntimeError"
        for entry in state["audit_log"]
    )

    assert state["audit_log"][-1]["new_status"] == "failed"

    mock_executor.assert_called_once()


    state = result["investigation_state"]

    assert state["tool_attempts"] == 1
    assert state["tool_calls_used"] == 0

    assert any(
        entry.get("event") == "tool_attempt"
        for entry in state["audit_log"]
    )

    assert state["status"] == "failed"


def test_no_tool_selection_completes_without_execution():
    """Verify no-tool investigations finish with an audit trail."""

    alert = {
        "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
        "source_ip": "198.51.100.75",
        "severity": "medium",
    }

    selection = {
        "tool_name": None,
        "parameters": {},
    }

    with patch(
        "src.agents.agentic_workflow.select_investigation_tool",
        return_value=selection,
    ), patch(
        "src.agents.agentic_workflow.execute_tool",
    ) as mock_executor:

        result = run_agentic_investigation(alert)

    state = result["investigation_state"]

    assert result["status"] == "no_tool_selected"
    assert result["tool_execution"] is None

    assert state["status"] == "completed"
    assert state["current_step"] == "no_tool_selected"
    assert state["completed_at"] is not None

    assert state["tool_calls_used"] == 0
    assert state["tool_executions"] == []

    assert [
        entry["new_status"]
        for entry in state["audit_log"]
        if "new_status" in entry
    ] == [
        "selecting_tool",
        "completed",
    ]

    mock_executor.assert_not_called()