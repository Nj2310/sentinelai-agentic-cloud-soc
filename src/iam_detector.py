from iam_parser import parse_iam_events


def detect_suspicious_iam_activity(events):
    """Identify IAM access key creation events for investigation."""

    alerts = []

    for event in events:
        actor = event.get("actor")
        target_user = event.get("target_user")

        if (
            actor
            and target_user
            and actor == target_user
        ):
            alert = {
                "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
                "severity": "medium",
                "timestamp": event.get("timestamp"),
                "source_ip": event.get("source_ip"),
                "actor": actor,
                "target_user": target_user,
                "reason": (
                    "IAM user created an access key for their "
                    "own account. Review whether this was authorized."
                ),
                "status": "needs_investigation",
            }

            alerts.append(alert)

    return alerts


if __name__ == "__main__":
    events = parse_iam_events()
    alerts = detect_suspicious_iam_activity(events)

    print("\nSentinelAI - IAM Security Detection Results")
    print("=" * 55)
    print(f"Total IAM alerts: {len(alerts)}")

    for alert in alerts:
        print(f"\nAlert Type: {alert['alert_type']}")
        print(f"Severity: {alert['severity']}")
        print(f"Actor: {alert['actor']}")
        print(f"Source IP: {alert['source_ip']}")
        print(f"Reason: {alert['reason']}")