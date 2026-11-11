from src.agents.investigation_tools import lookup_login_activity


TOOL_REGISTRY = {
    "lookup_login_activity": {
        "function": lookup_login_activity,
        "description": (
            "Look up AWS CloudTrail ConsoleLogin events "
            "associated with a specific source IP address."
        ),
        "required_parameters": ["source_ip"],
        "read_only": True,
    }
}


def get_available_tools():
    """Return metadata for approved investigation tools."""
    return {
        name: {
            "description": tool["description"],
            "required_parameters": tool["required_parameters"],
            "read_only": tool["read_only"],
        }
        for name, tool in TOOL_REGISTRY.items()
    }