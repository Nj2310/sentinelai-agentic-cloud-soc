import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IAM_LOG_FILE = (
    PROJECT_ROOT
    / "data"
    / "cloudtrail"
    / "iam"
    / "iam_access_key_events.json"
)


def parse_iam_events(log_file=IAM_LOG_FILE):
    """Extract IAM CreateAccessKey events from CloudTrail logs."""

    with open(log_file, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get("Records", [])
    iam_events = []

    for record in records:
        if (
            record.get("eventSource") == "iam.amazonaws.com"
            and record.get("eventName") == "CreateAccessKey"
        ):
            event = {
                "timestamp": record.get("eventTime"),
                "event_name": record.get("eventName"),
                "source_ip": record.get("sourceIPAddress"),
                "actor": (
                    record.get("userIdentity") or {}
                ).get("userName"),
                "target_user": (
                    record.get("requestParameters") or {}
                ).get("userName"),
            }

            iam_events.append(event)

    print("=" * 55)
    print("SentinelAI - AWS IAM Event Parser")
    print("=" * 55)
    print(f"Total CloudTrail records: {len(records)}")
    print(f"CreateAccessKey events: {len(iam_events)}")

    return iam_events


if __name__ == "__main__":
    events = parse_iam_events()

    print("\nNormalized IAM events:")
    print(json.dumps(events, indent=4))