import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from iam_parser import parse_iam_events
from iam_detector import detect_suspicious_iam_activity


def test_iam_self_access_key_creation():
    events = parse_iam_events()
    alerts = detect_suspicious_iam_activity(events)

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "IAM_SELF_ACCESS_KEY_CREATION"
    assert alerts[0]["actor"] == "compromised-user"
    assert alerts[0]["severity"] == "medium"
    assert alerts[0]["status"] == "needs_investigation"


def test_iam_admin_creating_key_for_another_user():
    events = [
        {
            "timestamp": "2026-11-09T14:00:00Z",
            "event_name": "CreateAccessKey",
            "source_ip": "192.0.2.10",
            "actor": "security-admin",
            "target_user": "service-account",
        }
    ]

    alerts = detect_suspicious_iam_activity(events)

    assert alerts == []