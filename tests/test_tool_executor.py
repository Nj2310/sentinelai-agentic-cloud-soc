import pytest
from unittest.mock import patch

from src.agents.tool_executor import execute_tool


def test_approved_tool_execution():
    mock_result = {
        "source_ip": "198.51.100.50",
        "event_count": 5,
        "matching_events": [],
    }

    with patch(
        # "src.agents.tool_registry.TOOL_REGISTRY"
        # "['lookup_login_activity']['function']",
        # return_value=mock_result,
        "src.agents.tool_executor.TOOL_REGISTRY",
        {
            "lookup_login_activity": {
                "function": lambda **kwargs: mock_result,
                "description": "Mock login lookup",
                "required_parameters": ["source_ip"],
                "read_only": True,
            }
        },
    ):
        # as mock_lookup:
        result = execute_tool(
            "lookup_login_activity",
            {"source_ip": "198.51.100.50"},
        )

    assert result["status"] == "success"
    assert result["result"]["event_count"] == 5
    # mock_lookup.assert_called_once_with(
    #     source_ip="198.51.100.50"
    # )


def test_unauthorized_tool_rejected():
    with pytest.raises(ValueError, match="Unauthorized tool"):
        execute_tool("delete_iam_user", {"username": "test-admin"})


def test_missing_parameter_rejected():
    with pytest.raises(ValueError, match="Missing required parameter"):
        execute_tool("lookup_login_activity", {})


def test_unexpected_parameter_rejected():
    with pytest.raises(ValueError, match="Unexpected parameters"):
        execute_tool(
            "lookup_login_activity",
            {
                "source_ip": "198.51.100.50",
                "delete_logs": True,
            },
        )