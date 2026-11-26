from src.agents.tool_registry import TOOL_REGISTRY
from src.agents.mcp_client import execute_mcp_tool


def execute_tool(tool_name: str, parameters: dict) -> dict:
    """
    Execute an approved, read-only investigation tool
    through the MCP client.
    """

    # Reject tools that are not registered.
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unauthorized tool: {tool_name}")

    tool = TOOL_REGISTRY[tool_name]

    # Enforce the read-only execution policy.
    if tool["read_only"] is not True:
        raise PermissionError(
            f"Tool is not approved for read-only execution: {tool_name}"
        )

    # Validate the parameter container.
    if not isinstance(parameters, dict):
        raise ValueError("Tool parameters must be a dictionary")

    # Validate required parameters.
    for parameter in tool["required_parameters"]:
        if parameter not in parameters:
            raise ValueError(
                f"Missing required parameter: {parameter}"
            )

    # Reject unexpected parameters.
    unexpected = set(parameters) - set(
        tool["required_parameters"]
    )

    if unexpected:
        raise ValueError(
            f"Unexpected parameters: {sorted(unexpected)}"
        )

    # Execute through the approved MCP communication path.
    # MCP failures propagate to the investigation workflow.
    # No direct local execution fallback is permitted.
    result = execute_mcp_tool(
        tool_name=tool_name,
        parameters=parameters,
    )

    return {
        "tool_name": tool_name,
        "parameters": parameters,
        "result": result,
        "status": "success",
        "execution_backend": "mcp_stdio",
    }