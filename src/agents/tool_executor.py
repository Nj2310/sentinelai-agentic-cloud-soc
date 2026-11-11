from src.agents.tool_registry import TOOL_REGISTRY


def execute_tool(tool_name: str, parameters: dict) -> dict:
    """
    Execute an approved, read-only investigation tool.
    """

    # Reject tools that are not registered.
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unauthorized tool: {tool_name}")

    tool = TOOL_REGISTRY[tool_name]

    # Prevent execution of tools not marked read-only.
    if not tool["read_only"]:
        raise PermissionError(
            f"Tool is not approved for read-only execution: {tool_name}"
        )

    # Validate required parameters.
    for parameter in tool["required_parameters"]:
        if parameter not in parameters:
            raise ValueError(
                f"Missing required parameter: {parameter}"
            )

    # Reject unexpected parameters.
    unexpected = set(parameters) - set(tool["required_parameters"])

    if unexpected:
        raise ValueError(
            f"Unexpected parameters: {sorted(unexpected)}"
        )

    # Execute the approved investigation function.
    result = tool["function"](**parameters)

    return {
        "tool_name": tool_name,
        "parameters": parameters,
        "result": result,
        "status": "success",
    }