import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "agents"))

from investigator import investigate_alert


def test_investigator_handles_no_matching_login_events():
    alert = {
        "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
        "actor": "compromised-user",
        "source_ip": "198.51.100.75",
        "severity": "medium",
    }

    mock_evidence = {
        "source_ip": "198.51.100.75",
        "event_count": 0,
        "matching_events": [],
    }

    with patch(
        "investigator.lookup_login_activity",
        return_value=mock_evidence,
    ) as mock_lookup:
        result = investigate_alert(alert)

    mock_lookup.assert_called_once_with("198.51.100.75")

    assert result["alert_type"] == "IAM_SELF_ACCESS_KEY_CREATION"
    assert result["login_evidence"]["event_count"] == 0
    assert result["login_evidence"]["matching_events"] == []
    assert result["status"] == "investigation_complete"

    assert any(
        "No matching login events found" in finding
        for finding in result["findings"]
    )


def test_investigator_with_ai():
    from unittest.mock import patch
    from src.agents.investigator import investigate_alert

    alert = {
        "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
        "actor": "test-user",
        "source_ip": "198.51.100.75",
        "severity": "medium",
    }

    with (
        patch(
            "src.agents.investigator.lookup_login_activity",
            return_value={
                "event_count": 0,
                "matching_events": [],
            },
        ),
        patch(
            "src.agents.investigator.generate_security_analysis",
            return_value="Suspicious activity requires analyst review.",
        ) as mock_ai,
    ):
        result = investigate_alert(alert, use_ai=True)

    assert result["status"] == "investigation_complete"
    assert result["login_evidence"]["event_count"] == 0
    assert result["ai_analysis"] == (
        "Suspicious activity requires analyst review."
    )

    mock_ai.assert_called_once()
    assert mock_ai.call_args.args[0]["alert_type"] == (
        "IAM_SELF_ACCESS_KEY_CREATION"
    )