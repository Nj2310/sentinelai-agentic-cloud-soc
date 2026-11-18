# import json
# from pathlib import Path


# def save_audit_log(state: dict, file_path: str | Path) -> None:
#     """
#     Append investigation audit events to a JSONL file.

#     Each line contains one JSON record.
#     """

#     if not isinstance(state, dict):
#         raise TypeError("Investigation state must be a dictionary.")

#     investigation_id = state["investigation_id"]
#     audit_log = state["audit_log"]

#     if not isinstance(audit_log, list):
#         raise TypeError("Audit log must be a list.")

#     path = Path(file_path)

#     # Create the destination directory if necessary.
#     path.parent.mkdir(parents=True, exist_ok=True)

#     with path.open("a", encoding="utf-8") as audit_file:
#         for entry in audit_log:
#             record = {
#                 "investigation_id": investigation_id,
#                 **entry,
#             }

#             audit_file.write(json.dumps(record) + "\n")

import json
from pathlib import Path


def save_audit_log(state: dict, file_path: str | Path) -> None:
    """
    Save investigation audit events to a JSONL file.

    Avoid duplicating events when the same investigation
    is saved multiple times.
    """

    if not isinstance(state, dict):
        raise TypeError("Investigation state must be a dictionary.")

    investigation_id = state["investigation_id"]
    audit_log = state["audit_log"]

    if not isinstance(audit_log, list):
        raise TypeError("Audit log must be a list.")

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Identify previously saved events.
    saved_events = set()

    if path.exists():
        with path.open("r", encoding="utf-8") as audit_file:
            for line in audit_file:
                if not line.strip():
                    continue

                record = json.loads(line)

                saved_events.add((
                    record.get("investigation_id"),
                    record.get("event_index"),
                ))

    # Append only events that have not been saved.
    with path.open("a", encoding="utf-8") as audit_file:
        for index, entry in enumerate(audit_log):
            event_key = (investigation_id, index)

            if event_key in saved_events:
                continue

            record = {
                **entry,
                "investigation_id": investigation_id,
                "event_index": index,
            }

            audit_file.write(json.dumps(record) + "\n")
            saved_events.add(event_key)