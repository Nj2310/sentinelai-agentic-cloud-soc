import json

from src.agents.audit_storage import save_audit_log
from src.agents.investigation_state import (
    create_investigation_state,
    update_investigation_state,
)


def test_save_audit_log_writes_jsonl(tmp_path):
    # Create a synthetic investigation.
    alert = {
        "alert_type": "brute_force",
        "source_ip": "192.0.2.10",
    }

    state = create_investigation_state(alert)

    # Generate an audit event.
    update_investigation_state(
        state,
        "selecting_tool",
        "select_investigation_tool",
    )

    # Save the audit log to a temporary file.
    audit_file = tmp_path / "audit.jsonl"

    save_audit_log(state, audit_file)

    # Read and validate the saved record.
    lines = audit_file.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    record = json.loads(lines[0])

    assert record["investigation_id"] == state["investigation_id"]
    assert record["previous_status"] == "initialized"
    assert record["new_status"] == "selecting_tool"
    assert record["step"] == "select_investigation_tool"
    assert "timestamp" in record

def test_save_audit_log_does_not_duplicate_events(tmp_path):
    alert = {
        "alert_type": "brute_force",
        "source_ip": "192.0.2.10",
    }

    state = create_investigation_state(alert)

    update_investigation_state(
        state,
        "selecting_tool",
        "select_investigation_tool",
    )

    audit_file = tmp_path / "audit.jsonl"

    # Simulate saving the same investigation twice.
    save_audit_log(state, audit_file)
    save_audit_log(state, audit_file)

    lines = audit_file.read_text(
        encoding="utf-8"
    ).splitlines()

    # The same event should only be stored once.
    assert len(lines) == 1

def test_save_audit_log_appends_only_new_events(tmp_path):
    state = create_investigation_state({
        "alert_type": "brute_force",
        "source_ip": "192.0.2.10",
    })

    audit_file = tmp_path / "audit.jsonl"

    # First investigation transition.
    update_investigation_state(
        state,
        "selecting_tool",
        "select_investigation_tool",
    )

    save_audit_log(state, audit_file)

    # Second investigation transition.
    update_investigation_state(
        state,
        "executing_tool",
        "execute_investigation_tool",
    )

    save_audit_log(state, audit_file)

    # Read the persisted audit history.
    lines = audit_file.read_text(
        encoding="utf-8"
    ).splitlines()

    records = [json.loads(line) for line in lines]

    assert len(records) == 2

    assert records[0]["event_index"] == 0
    assert records[0]["new_status"] == "selecting_tool"

    assert records[1]["event_index"] == 1
    assert records[1]["new_status"] == "executing_tool"

    assert all(
        record["investigation_id"] == state["investigation_id"]
        for record in records
    )