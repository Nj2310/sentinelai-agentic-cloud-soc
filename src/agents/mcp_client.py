import asyncio
import ipaddress
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

MCP_TIMEOUT_SECONDS = 30

MCP_TOOL_MAPPING = {
    "lookup_login_activity": "lookup_login_activity_mcp",
}


class MCPExecutionError(RuntimeError):
    """Raised when an MCP investigation cannot complete safely."""


def validate_source_ip(source_ip: str) -> str:
    """Validate and normalize an investigation source IP."""

    if not isinstance(source_ip, str) or not source_ip.strip():
        raise ValueError("A valid source IP address is required")

    try:
        return str(ipaddress.ip_address(source_ip))
    except ValueError as exc:
        raise ValueError("Invalid source IP address") from exc


def validate_mcp_response(data: dict, expected_ip: str) -> dict:
    """Validate the investigation evidence returned by MCP."""

    if not isinstance(data, dict):
        raise MCPExecutionError("Invalid MCP response format")

    required_fields = {
        "source_ip",
        "matching_events",
        "event_count",
    }

    if not required_fields.issubset(data):
        raise MCPExecutionError("Missing required MCP response fields")

    if data["source_ip"] != expected_ip:
        raise MCPExecutionError("MCP response source IP mismatch")

    events = data["matching_events"]
    event_count = data["event_count"]

    if not isinstance(events, list):
        raise MCPExecutionError("Invalid matching events format")

    if type(event_count) is not int or event_count < 0:
        raise MCPExecutionError("Invalid MCP event count")

    if event_count != len(events):
        raise MCPExecutionError("MCP event count mismatch")

    for event in events:
        if not isinstance(event, dict):
            raise MCPExecutionError("Invalid investigation event")

        if event.get("source_ip") != expected_ip:
            raise MCPExecutionError(
                "Investigation event source IP mismatch"
            )

    return {
        "source_ip": expected_ip,
        "matching_events": events,
        "event_count": event_count,
    }


async def call_mcp_tool(
    tool_name: str,
    parameters: dict,
) -> dict:
    """Execute an approved investigation through MCP STDIO."""

    if tool_name not in MCP_TOOL_MAPPING:
        raise ValueError(f"Unauthorized MCP tool: {tool_name}")

    if not isinstance(parameters, dict):
        raise ValueError("MCP parameters must be a dictionary")

    if set(parameters) != {"source_ip"}:
        raise ValueError("Invalid MCP tool parameters")

    validated_ip = validate_source_ip(parameters["source_ip"])

    mcp_tool_name = MCP_TOOL_MAPPING[tool_name]

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.agents.mcp_server"],
        cwd=str(PROJECT_ROOT),
    )

    try:
        async with asyncio.timeout(MCP_TIMEOUT_SECONDS):

            async with stdio_client(server_params) as (read, write):

                async with ClientSession(read, write) as session:

                    await session.initialize()

                    available_tools = await session.list_tools()

                    tool_names = {
                        tool.name
                        for tool in available_tools.tools
                    }

                    if mcp_tool_name not in tool_names:
                        raise MCPExecutionError(
                            "Approved MCP tool is unavailable"
                        )

                    response = await session.call_tool(
                        mcp_tool_name,
                        {"source_ip": validated_ip},
                    )

                    if response.isError:
                        raise MCPExecutionError(
                            "MCP server rejected the investigation"
                        )

                    if len(response.content) != 1:
                        raise MCPExecutionError(
                            "Unexpected MCP response content"
                        )

                    text = getattr(
                        response.content[0],
                        "text",
                        None,
                    )

                    if not isinstance(text, str):
                        raise MCPExecutionError(
                            "MCP response does not contain text"
                        )

                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError as exc:
                        raise MCPExecutionError(
                            "Invalid JSON returned by MCP server"
                        ) from exc

                    return validate_mcp_response(
                        data,
                        validated_ip,
                    )

    except TimeoutError as exc:
        raise MCPExecutionError(
            "MCP investigation timed out"
        ) from exc

    except MCPExecutionError:
        raise

    except Exception as exc:
        raise MCPExecutionError(
            f"MCP communication failed: {type(exc).__name__}"
        ) from exc


def execute_mcp_tool(
    tool_name: str,
    parameters: dict,
) -> dict:
    """Synchronous interface for the agentic investigation workflow."""

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            call_mcp_tool(tool_name, parameters)
        )

    raise MCPExecutionError(
        "Synchronous MCP execution cannot run "
        "inside an active asynchronous event loop"
    )