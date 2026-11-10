import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from iam_parser import parse_iam_events
from iam_detector import detect_suspicious_iam_activity
# from investigation_tools import lookup_login_activity
from src.agents.investigation_tools import lookup_login_activity
from src.agents.llm_client import generate_security_analysis

def investigate_alert(alert, use_ai=False):
    """Create a read-only, structured IAM investigation."""

    investigation = {
        "alert_type": alert.get("alert_type"),
        "actor": alert.get("actor"),
        "source_ip": alert.get("source_ip"),
        "severity": alert.get("severity"),
        "findings": [],
        "recommended_actions": [],
        "status": "investigation_complete",
    }

    if alert.get("alert_type") == "IAM_SELF_ACCESS_KEY_CREATION":
        investigation["findings"].append(
            "IAM user created an access key for their own account."
        )

        investigation["recommended_actions"].extend([
            "Verify whether the access key creation was authorized.",
            "Review recent CloudTrail activity for the IAM user.",
            "Check for unusual source IP addresses or login activity.",
        ])
    
    source_ip = alert.get("source_ip")

    if source_ip:
        login_evidence = lookup_login_activity(source_ip)

        investigation["login_evidence"] = {
            "source_ip": source_ip,
            "event_count": login_evidence["event_count"],
            "matching_events": login_evidence["matching_events"],
        }

        if login_evidence["event_count"] > 0:
            investigation["findings"].append(
                f"Found {login_evidence['event_count']} "
                "login events associated with the alert source IP."
            )
        else:
            investigation["findings"].append(
                "No matching login events found in the available "
                "CloudTrail dataset for this source IP."
            )
        if use_ai:
            investigation["ai_analysis"] = generate_security_analysis(
                investigation
        )

    return investigation


if __name__ == "__main__":
    events = parse_iam_events()
    alerts = detect_suspicious_iam_activity(events)

    print("\nSentinelAI - SOC Investigation Results")
    print("=" * 55)

    for alert in alerts:
        result = investigate_alert(alert)
        print(json.dumps(result, indent=4))