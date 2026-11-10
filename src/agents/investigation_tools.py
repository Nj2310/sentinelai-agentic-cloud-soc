import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cloudtrail_parser import parse_cloudtrail_logs


def lookup_login_activity(source_ip):
    """Find CloudTrail login events associated with a source IP."""

    events = parse_cloudtrail_logs()

    matching_events = [
        event
        for event in events
        if event.get("source_ip") == source_ip
    ]

    return {
        "source_ip": source_ip,
        "matching_events": matching_events,
        "event_count": len(matching_events),
    }


if __name__ == "__main__":
    result = lookup_login_activity("198.51.100.50")

    print("\nSentinelAI - Login Activity Investigation")
    print("=" * 55)
    print(f"Source IP: {result['source_ip']}")
    print(f"Matching events: {result['event_count']}")

    for event in result["matching_events"]:
        print(event)