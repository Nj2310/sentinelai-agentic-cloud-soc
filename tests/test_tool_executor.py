import pytest
from unittest.mock import patch, Mock

from src.agents.tool_executor import execute_tool
from src.agents.mcp_client import MCPExecutionError


def test_approved_tool_execution():
    mock_result = {
        "source_ip": "198.51.100.50",
        "event_count": 1,
        "matching_events": [
            {
                "timestamp": "2026-11-08 10:00:00",
                "source_ip": "198.51.100.50",
                "username": "test-admin",
                "status": "Failure",
            }
        ],
    }

    with patch(
        "src.agents.tool_executor.execute_mcp_tool",
        return_value=mock_result,
    ) as mock_mcp:

        result = execute_tool(
            "lookup_login_activity",
            {"source_ip": "198.51.100.50"},
        )

    assert result["status"] == "success"
    assert result["result"] == mock_result
    assert result["execution_backend"] == "mcp_stdio"

    mock_mcp.assert_called_once_with(
        tool_name="lookup_login_activity",
        parameters={"source_ip": "198.51.100.50"},
    )


def test_unauthorized_tool_rejected():
    with patch(
        "src.agents.tool_executor.execute_mcp_tool"
    ) as mock_mcp:

        with pytest.raises(ValueError, match="Unauthorized tool"):
            execute_tool(
                "delete_iam_user",
                {"username": "test-admin"},
            )

        mock_mcp.assert_not_called()


def test_missing_parameter_rejected():
    with patch(
        "src.agents.tool_executor.execute_mcp_tool"
    ) as mock_mcp:

        with pytest.raises(
            ValueError,
            match="Missing required parameter",
        ):
            execute_tool("lookup_login_activity", {})

        mock_mcp.assert_not_called()


def test_unexpected_parameter_rejected():
    with patch(
        "src.agents.tool_executor.execute_mcp_tool"
    ) as mock_mcp:

        with pytest.raises(
            ValueError,
            match="Unexpected parameters",
        ):
            execute_tool(
                "lookup_login_activity",
                {
                    "source_ip": "198.51.100.50",
                    "delete_logs": True,
                },
            )

        mock_mcp.assert_not_called()


def test_non_read_only_tool_rejected():
    mock_registry = {
        "lookup_login_activity": {
            "function": Mock(),
            "description": "Unauthorized write-capable tool",
            "required_parameters": ["source_ip"],
            "read_only": False,
        }
    }

    with patch(
        "src.agents.tool_executor.TOOL_REGISTRY",
        mock_registry,
    ), patch(
        "src.agents.tool_executor.execute_mcp_tool"
    ) as mock_mcp:

        with pytest.raises(
            PermissionError,
            match="not approved for read-only execution",
        ):
            execute_tool(
                "lookup_login_activity",
                {"source_ip": "198.51.100.50"},
            )

        mock_mcp.assert_not_called()

    mock_registry["lookup_login_activity"][
        "function"
    ].assert_not_called()


def test_invalid_parameter_container_rejected():
    with patch(
        "src.agents.tool_executor.execute_mcp_tool"
    ) as mock_mcp:

        with pytest.raises(
            ValueError,
            match="Tool parameters must be a dictionary",
        ):
            execute_tool(
                "lookup_login_activity",
                ["198.51.100.50"],
            )

        mock_mcp.assert_not_called()


def test_mcp_failure_does_not_fallback_to_local_execution():
    mock_local_function = Mock()

    mock_registry = {
        "lookup_login_activity": {
            "function": mock_local_function,
            "description": "Read-only login lookup",
            "required_parameters": ["source_ip"],
            "read_only": True,
        }
    }

    with patch(
        "src.agents.tool_executor.TOOL_REGISTRY",
        mock_registry,
    ), patch(
        "src.agents.tool_executor.execute_mcp_tool",
        side_effect=MCPExecutionError(
            "MCP communication failed"
        ),
    ) as mock_mcp:

        with pytest.raises(
            MCPExecutionError,
            match="MCP communication failed",
        ):
            execute_tool(
                "lookup_login_activity",
                {"source_ip": "198.51.100.50"},
            )

        mock_mcp.assert_called_once()
        mock_local_function.assert_not_called()