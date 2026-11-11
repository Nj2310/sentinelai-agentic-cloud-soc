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

    execution = {
        "tool_name": "lookup_login_activity",
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