# from src.agents.tool_selector import select_investigation_tool
# from src.agents.tool_executor import execute_tool


# def run_agentic_investigation(alert: dict) -> dict:
#     """Run a controlled, read-only AI investigation workflow."""

#     selection = select_investigation_tool(alert)

#     if selection["tool_name"] is None:
#         return {
#             "alert": alert,
#             "selection": selection,
#             "tool_execution": None,
#             "status": "no_tool_selected",
#         }

#     execution = execute_tool(
#         tool_name=selection["tool_name"],
#         parameters=selection["parameters"],
#     )

#     return {
#         "alert": alert,
#         "selection": selection,
#         "tool_execution": execution,
#         "status": "completed",
#     }


from src.agents.tool_selector import select_investigation_tool
from src.agents.tool_executor import execute_tool
from src.agents.investigation_state import (
    create_investigation_state,
    update_investigation_state,
    record_tool_execution,
    record_tool_attempt,
)


def run_agentic_investigation(alert: dict) -> dict:
    """Run a controlled, auditable, read-only AI investigation."""

    state = create_investigation_state(alert)
    selection = None

    try:
        # Step 1: Select an approved investigation tool.
        update_investigation_state(
            state, "selecting_tool", "tool_selection"
        )

        selection = select_investigation_tool(alert)

        # Step 2: Handle investigations requiring no tool.
        if selection["tool_name"] is None:
            update_investigation_state(
                state, "completed", "no_tool_selected"
            )

            return {
                "alert": alert,
                "selection": selection,
                "tool_execution": None,
                "status": "no_tool_selected",
                "investigation_state": state,
            }

        # Step 3: Enforce the execution limit BEFORE tool invocation.
        # if state["tool_calls_used"] >= state["max_tool_calls"]:
        #     raise RuntimeError(
        #         "Investigation tool execution limit reached."
        #     )

        if state["tool_attempts"] >= state["max_tool_calls"]:
            raise RuntimeError(
                "Investigation tool attempt limit reached."
            )


        update_investigation_state(
            state, "executing_tool", "tool_execution"
        )

        record_tool_attempt(
            state,
            selection["tool_name"]
        )

        # Step 4: Execute the approved read-only tool.
        execution = execute_tool(
            tool_name=selection["tool_name"],
            parameters=selection["parameters"],
        )

        # Step 5: Record execution evidence and audit activity.
        record_tool_execution(state, execution)

        # Step 6: Complete the investigation.
        update_investigation_state(
            state, "completed", "investigation_complete"
        )

        return {
            "alert": alert,
            "selection": selection,
            "tool_execution": execution,
            "status": "completed",
            "investigation_state": state,
        }

    except Exception as error:
        # Preserve the error in the audit trail.
        state["audit_log"].append({
            "event": "investigation_error",
            "error_type": type(error).__name__,
        })

        if state["status"] not in {"completed", "failed"}:
            update_investigation_state(
                state, "failed", "investigation_failed"
            )

        return {
            "alert": alert,
            "selection": selection,
            "tool_execution": None,
            "status": "failed",
            "error": str(error),
            "investigation_state": state,
        }