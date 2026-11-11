from src.agents.tool_selector import select_investigation_tool
from src.agents.tool_executor import execute_tool


def run_agentic_investigation(alert: dict) -> dict:
    """Run a controlled, read-only AI investigation workflow."""

    selection = select_investigation_tool(alert)

    if selection["tool_name"] is None:
        return {
            "alert": alert,
            "selection": selection,
            "tool_execution": None,
            "status": "no_tool_selected",
        }

    execution = execute_tool(
        tool_name=selection["tool_name"],
        parameters=selection["parameters"],
    )

    return {
        "alert": alert,
        "selection": selection,
        "tool_execution": execution,
        "status": "completed",
    }