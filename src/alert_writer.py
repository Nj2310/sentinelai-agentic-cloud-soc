import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Locate the project's alerts folder
BASE_DIR = Path(__file__).resolve().parent.parent
ALERTS_DIR = BASE_DIR / "alerts"


def save_alert(source_ip, failed_attempts, detection_time):
    """Save a detected security alert as a JSON file."""

    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    # Check existing alerts to prevent duplicates
    for alert_file in ALERTS_DIR.glob("*.json"):
        with open(alert_file, "r", encoding="utf-8") as file:
            existing_alert = json.load(file)

        if (
            existing_alert.get("source_ip") == source_ip
            and existing_alert.get("alert_type") == "Brute Force"
            and existing_alert.get("detection_time") == detection_time
            and existing_alert.get("mitre_attack") == "T1110"
        ):
            print(f"Duplicate alert skipped for IP: {source_ip}")
            return None

    alert = {
        "alert_id": str(uuid4()),
        "alert_type": "Brute Force",
        "severity": "HIGH",
        "source_ip": source_ip,
        "failed_attempts": failed_attempts,
        "detection_time": detection_time,
        "mitre_attack": "T1110",
        "recommended_action": "Investigate authentication activity.",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    filename = f"alert_{alert['alert_id']}.json"
    alert_path = ALERTS_DIR / filename

    with open(alert_path, "w", encoding="utf-8") as file:
        json.dump(alert, file, indent=4)

    print(f"Security alert saved: {alert_path}")

    return alert_path