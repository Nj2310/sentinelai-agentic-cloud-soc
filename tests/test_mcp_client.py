import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

import pytest

from src.agents.mcp_client import (
    MCPExecutionError,
    validate_source_ip,
    validate_mcp_response,
    call_mcp_tool,
    execute_mcp_tool,
)


SOURCE_IP = "198.51.100.50"
TOOL_NAME = "lookup_login_activity"


def make_valid_response():
    return {
        "source_ip": SOURCE_IP,
        "matching_events": [
            {
                "timestamp": "2026-11-08 10:00:00",
                "source_ip": SOURCE_IP,
                "username": "test-admin",
                "status": "Failure",
            }
        ],
        "event_count": 1,
    }


def test_valid_source_ip():
    assert validate_source_ip(SOURCE_IP) == SOURCE_IP


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "",
        "198.5:100.50",
        "999.999.999.999",
        None,
        12345,
        "example.com",
    ],
)
def test_invalid_source_ip_rejected(invalid_ip):
    with pytest.raises(ValueError):
        validate_source_ip(invalid_ip)


def test_valid_mcp_response():
    response = make_valid_response()

    assert validate_mcp_response(
        response, SOURCE_IP
    ) == response


def test_empty_investigation_result_is_valid():
    response = {
        "source_ip": SOURCE_IP,
        "matching_events": [],
        "event_count": 0,
    }

    assert validate_mcp_response(
        response, SOURCE_IP
    ) == response


def test_non_dictionary_response_rejected():
    with pytest.raises(MCPExecutionError):
        validate_mcp_response([], SOURCE_IP)


def test_missing_response_fields_rejected():
    response = make_valid_response()
    del response["event_count"]

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_response_source_ip_mismatch_rejected():
    response = make_valid_response()
    response["source_ip"] = "203.0.113.10"

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_event_source_ip_mismatch_rejected():
    response = make_valid_response()

    response["matching_events"][0][
        "source_ip"
    ] = "203.0.113.10"

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_event_count_mismatch_rejected():
    response = make_valid_response()
    response["event_count"] = 99

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


@pytest.mark.parametrize(
    "invalid_count",
    [-1, True, "1", 1.5],
)
def test_invalid_event_count_rejected(invalid_count):
    response = make_valid_response()
    response["event_count"] = invalid_count

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_invalid_event_collection_rejected():
    response = make_valid_response()
    response["matching_events"] = "invalid"

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_invalid_event_object_rejected():
    response = make_valid_response()
    response["matching_events"] = ["invalid"]

    with pytest.raises(MCPExecutionError):
        validate_mcp_response(response, SOURCE_IP)


def test_unauthorized_mcp_tool_rejected():
    with patch(
        "src.agents.mcp_client.stdio_client"
    ) as mock_transport:

        with pytest.raises(
            ValueError,
            match="Unauthorized MCP tool",
        ):
            execute_mcp_tool(
                "delete_iam_user",
                {"username": "test-admin"},
            )

        mock_transport.assert_not_called()


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"source_ip": SOURCE_IP, "delete_logs": True},
        {"source_ip": "invalid-ip"},
        [SOURCE_IP],
    ],
)
def test_invalid_mcp_parameters_rejected(parameters):
    with patch(
        "src.agents.mcp_client.stdio_client"
    ) as mock_transport:

        with pytest.raises(ValueError):
            execute_mcp_tool(
                TOOL_NAME,
                parameters,
            )

        mock_transport.assert_not_called()


def test_active_event_loop_rejected():
    async def run_test():
        with pytest.raises(MCPExecutionError):
            execute_mcp_tool(
                TOOL_NAME,
                {"source_ip": SOURCE_IP},
            )

    asyncio.run(run_test())


def test_mcp_communication_failure():
    with patch(
        "src.agents.mcp_client.stdio_client",
        side_effect=OSError("Transport unavailable"),
    ):
        with pytest.raises(MCPExecutionError):
            execute_mcp_tool(
                TOOL_NAME,
                {"source_ip": SOURCE_IP},
            )


def test_mcp_timeout():
    @asynccontextmanager
    async def slow_transport(*args, **kwargs):
        await asyncio.sleep(1)
        yield None, None

    with patch(
        "src.agents.mcp_client.stdio_client",
        slow_transport,
    ), patch(
        "src.agents.mcp_client.MCP_TIMEOUT_SECONDS",
        0.01,
    ):
        with pytest.raises(
            MCPExecutionError,
            match="timed out",
        ):
            execute_mcp_tool(
                TOOL_NAME,
                {"source_ip": SOURCE_IP},
            )


def make_mock_session(tool_names, response):
    session = SimpleNamespace(
        initialize=AsyncMock(),
        list_tools=AsyncMock(
            return_value=SimpleNamespace(
                tools=[
                    SimpleNamespace(name=name)
                    for name in tool_names
                ]
            )
        ),
        call_tool=AsyncMock(return_value=response),
    )

    return session


@asynccontextmanager
async def mock_transport(*args, **kwargs):
    yield None, None


def test_approved_mcp_tool_unavailable():
    session = make_mock_session([], None)

    @asynccontextmanager
    async def mock_session(*args, **kwargs):
        yield session

    with patch(
        "src.agents.mcp_client.stdio_client",
        mock_transport,
    ), patch(
        "src.agents.mcp_client.ClientSession",
        mock_session,
    ):
        with pytest.raises(MCPExecutionError):
            asyncio.run(
                call_mcp_tool(
                    TOOL_NAME,
                    {"source_ip": SOURCE_IP},
                )
            )

    session.call_tool.assert_not_called()


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(
            isError=True,
            content=[],
        ),
        SimpleNamespace(
            isError=False,
            content=[],
        ),
        SimpleNamespace(
            isError=False,
            content=[
                SimpleNamespace(text="invalid JSON")
            ],
        ),
    ],
)
def test_invalid_mcp_server_response_rejected(response):
    session = make_mock_session(
        ["lookup_login_activity_mcp"],
        response,
    )

    @asynccontextmanager
    async def mock_session(*args, **kwargs):
        yield session

    with patch(
        "src.agents.mcp_client.stdio_client",
        mock_transport,
    ), patch(
        "src.agents.mcp_client.ClientSession",
        mock_session,
    ):
        with pytest.raises(MCPExecutionError):
            execute_mcp_tool(
                TOOL_NAME,
                {"source_ip": SOURCE_IP},
            )

    session.call_tool.assert_awaited_once()


def test_real_mcp_stdio_integration():
    result = execute_mcp_tool(
        TOOL_NAME,
        {"source_ip": SOURCE_IP},
    )

    assert result["source_ip"] == SOURCE_IP
    assert result["event_count"] == 5
    assert len(result["matching_events"]) == 5

    assert all(
        event["source_ip"] == SOURCE_IP
        for event in result["matching_events"]
    )