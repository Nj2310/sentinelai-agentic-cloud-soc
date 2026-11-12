from datetime import datetime, timezone
from uuid import uuid4


def create_investigation_state(alert: dict) -> dict:
    """
    Create an initial state for a security investigation.

    This function does not execute tools or call an LLM.
    """

    if not isinstance(alert, dict):
        raise TypeError("Alert must be a dictionary.")

    return {
        "investigation_id": str(uuid4()),
        "alert": alert.copy(),
        "status": "initialized",
        "current_step": "start",
        "tool_executions": [],
        "audit_log": [],
        "max_tool_calls": 1,
        "tool_calls_used": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }


def update_investigation_state(
    state: dict,
    new_status: str,
    step: str
) -> dict:
    """
    Update investigation progress and record the transition.

    This function does not execute tools or call an LLM.
    """

    allowed_statuses = {
        "initialized",
        "selecting_tool",
        "executing_tool",
        "completed",
        "failed",
    }

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid investigation status: {new_status}"
        )

    if state["status"] in {"completed", "failed"}:
        raise ValueError(
            "Cannot update a finished investigation."
        )

    previous_status = state["status"]

    state["status"] = new_status
    state["current_step"] = step

    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "previous_status": previous_status,
        "new_status": new_status,
        "step": step,
    }

    state["audit_log"].append(audit_entry)

    if new_status in {"completed", "failed"}:
        state["completed_at"] = audit_entry["timestamp"]

    return state


def record_tool_execution(
    state: dict,
    execution: dict
) -> dict:
    """
    Record an approved tool execution in the investigation state.

    Enforces the configured tool-call limit.
    """

    if state["status"] != "executing_tool":
        raise ValueError(
            "Tool execution can only be recorded "
            "during the executing_tool state."
        )

    if state["tool_calls_used"] >= state["max_tool_calls"]:
        raise RuntimeError(
            "Investigation tool execution limit reached."
        )

    if not isinstance(execution, dict):
        raise TypeError(
            "Tool execution record must be a dictionary."
        )

    required_fields = {
        "tool_name",
        "parameters",
        "result",
        "status",
    }

    if not required_fields.issubset(execution):
        raise ValueError(
            "Tool execution record is missing required fields."
        )

    if execution["status"] != "success":
        raise ValueError(
            "Only successful tool executions can be recorded."
        )

    timestamp = datetime.now(timezone.utc).isoformat()

    state["tool_executions"].append({
        "timestamp": timestamp,
        **execution,
    })

    state["tool_calls_used"] += 1

    state["audit_log"].append({
        "timestamp": timestamp,
        "event": "tool_execution",
        "tool_name": execution["tool_name"],
        "status": execution["status"],
    })

    return state