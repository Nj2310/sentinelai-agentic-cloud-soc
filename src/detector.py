import csv
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from alert_writer import save_alert


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_FILE = PROJECT_ROOT / "data" / "authentication_logs.csv"

FAILED_LOGIN_THRESHOLD = 5
TIME_WINDOW = timedelta(minutes=5)


def detect_brute_force(
    log_file=LOG_FILE,
    save_alerts=True,
    events=None,
    return_alerts=False,
):
    """
    Detect brute-force authentication activity.

    By default, return a set of suspicious IP addresses
    to preserve backward compatibility.

    When return_alerts=True, return structured alert
    dictionaries for SOC pipeline integration.
    """

    failed_attempts = defaultdict(deque)
    suspicious_ips = set()
    alerts = []

    # Load CSV events or use supplied normalized events.
    if events is None:
        with open(log_file, mode="r", encoding="utf-8") as file:
            raw_events = list(csv.DictReader(file))
    else:
        raw_events = events

    validated_events = []

    # Validate timestamps before chronological processing.
    for row in raw_events:
        try:
            timestamp = datetime.strptime(
                row["timestamp"],
                "%Y-%m-%d %H:%M:%S",
            )
        except (KeyError, ValueError, TypeError):
            print("Warning: Skipping event with invalid timestamp.")
            continue

        validated_events.append((timestamp, row))

    validated_events.sort(key=lambda item: item[0])

    for timestamp, event in validated_events:

        source_ip = (event.get("source_ip") or "").strip()
        status = (event.get("status") or "").strip().lower()

        if not source_ip:
            continue

        if status not in {"failure", "failed"}:
            continue

        attempts = failed_attempts[source_ip]
        attempts.append(timestamp)

        # Remove attempts outside the detection window.
        while attempts and timestamp - attempts[0] > TIME_WINDOW:
            attempts.popleft()

        # Generate one alert per suspicious IP per run.
        if (
            len(attempts) >= FAILED_LOGIN_THRESHOLD
            and source_ip not in suspicious_ips
        ):
            suspicious_ips.add(source_ip)

            alert = {
                "alert_id": str(uuid4()),
                "alert_type": "BRUTE_FORCE",
                "severity": "HIGH",
                "source_ip": source_ip,
                "failed_attempts": len(attempts),
                "detection_time": timestamp.isoformat(),
                "mitre_attack": "T1110",
                "recommended_action": (
                    "Investigate authentication activity."
                ),
                "status": "needs_investigation",
            }

            alerts.append(alert)

            print(
                f"HIGH: Potential brute-force activity "
                f"detected from {source_ip}"
            )
            print(f"Failed attempts: {len(attempts)}")
            print("MITRE ATT&CK: T1110")

            if save_alerts:
                save_alert(
                    source_ip,
                    len(attempts),
                    timestamp.isoformat(),
                )

    if return_alerts:
        return alerts

    return suspicious_ips


if __name__ == "__main__":
    detected_ips = detect_brute_force()

    print("\nSentinelAI - Detection Results")
    print("=" * 55)
    print(f"Suspicious IP addresses: {detected_ips}")