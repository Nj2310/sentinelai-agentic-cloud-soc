from datetime import datetime, timezone
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLOUDTRAIL_FILE = (
    PROJECT_ROOT / "data" / "cloudtrail" / "cloudtrail_login_events.json"
)


def parse_cloudtrail_logs(log_file=CLOUDTRAIL_FILE):
    """Read AWS CloudTrail JSON logs and extract login events."""

    with open(log_file, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get("Records", [])
    login_events = []

    for record in records:
        if (
            record.get("eventSource") == "signin.amazonaws.com"
            and record.get("eventName") == "ConsoleLogin"
        ):
            # login_events.append(record)
            login_event = {
                # "timestamp": record.get("eventTime"),
                                
                "timestamp": datetime.fromisoformat(
                    record["eventTime"].replace("Z", "+00:00")
                ).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),

                "source_ip": record.get("sourceIPAddress"),
                "username": (
                    record.get("userIdentity") or {}
                ).get("userName"),
                "status": (
                    record.get("responseElements") or {}
                ).get("ConsoleLogin"),
            }

            login_events.append(login_event)

    print("=" * 55)
    print("SentinelAI - AWS CloudTrail Log Parser")
    print("=" * 55)
    print(f"Total CloudTrail records: {len(records)}")
    print(f"Console login events: {len(login_events)}")

    return login_events


if __name__ == "__main__":
    # parse_cloudtrail_logs()
    
    # events = parse_cloudtrail_logs()

    # print("\nFirst normalized login event:")
    # print(json.dumps(events[0], indent=4))

    from detector import detect_brute_force

    events = parse_cloudtrail_logs()

    print("\nRunning SentinelAI detection on CloudTrail events...\n")

    detected_ips = detect_brute_force(
        events=events,
        save_alerts=False
    )

    print("\nCloudTrail detection results:")
    print(f"Suspicious IP addresses: {detected_ips}")