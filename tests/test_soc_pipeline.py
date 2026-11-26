import json
from unittest.mock import patch

from src.soc_pipeline import (
    normalize_iam_alert,
    investigate_alert,
    build_summary,
    save_soc_results,
    run_soc_pipeline,
)


def test_normalize_iam_alert():
    finding = {
        "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
        "severity": "medium",
        "source_ip": "198.51.100.75",
        "timestamp": "2026-11-09T14:05:00Z",
        "actor": "test-user",
        "target_user": "test-user",
        "reason": "Review access key creation.",
    }

    alert = normalize_iam_alert(finding)

    assert alert["alert_id"]
    assert alert["severity"] == "MEDIUM"
    assert alert["source_ip"] == "198.51.100.75"
    assert alert["actor"] == "test-user"
    assert alert["mitre_attack"] == "T1098.001"
    assert alert["status"] == "needs_investigation"


def test_iam_alert_requires_manual_review(tmp_path):
    alert = {
        "alert_id": "iam-test-001",
        "alert_type": "IAM_SELF_ACCESS_KEY_CREATION",
        "severity": "MEDIUM",
    }

    with patch(
        "src.soc_pipeline.run_agentic_investigation"
    ) as mock_investigation:

        result = investigate_alert(
            alert,
            tmp_path / "audit.jsonl",
        )

        mock_investigation.assert_not_called()

    assert result["alert_id"] == alert["alert_id"]
    assert result["status"] == "manual_review_required"
    assert result["selection"] is None
    assert result["tool_execution"] is None
    assert result["investigation_state"] is None


def test_brute_force_investigation_routing(tmp_path):
    alert = {
        "alert_id": "brute-force-test-001",
        "alert_type": "BRUTE_FORCE",
        "severity": "HIGH",
        "source_ip": "198.51.100.50",
    }

    audit_path = tmp_path / "audit.jsonl"

    mock_result = {
        "status": "completed",
        "selection": {
            "tool_name": "lookup_login_activity",
            "parameters": {
                "source_ip": "198.51.100.50",
            },
        },
        "tool_execution": {
            "status": "success",
        },
        "investigation_state": {
            "tool_attempts": 1,
            "max_tool_calls": 1,
        },
    }

    with patch(
        "src.soc_pipeline.run_agentic_investigation",
        return_value=mock_result,
    ) as mock_investigation:

        result = investigate_alert(alert, audit_path)

        mock_investigation.assert_called_once_with(
            alert=alert,
            audit_file_path=audit_path,
        )

    assert result["status"] == "completed"
    assert result["alert_id"] == alert["alert_id"]

    assert (
        result["selection"]["parameters"]["source_ip"]
        == alert["source_ip"]
    )


def test_investigation_exception_handling(tmp_path):
    alert = {
        "alert_id": "failed-test-001",
        "alert_type": "BRUTE_FORCE",
        "severity": "HIGH",
    }

    with patch(
        "src.soc_pipeline.run_agentic_investigation",
        side_effect=RuntimeError("Simulated failure"),
    ):
        result = investigate_alert(
            alert,
            tmp_path / "audit.jsonl",
        )

    assert result["status"] == "failed"
    assert result["error_type"] == "RuntimeError"
    assert result["tool_execution"] is None


def test_build_summary():
    alerts = [
        {"severity": "HIGH"},
        {"severity": "MEDIUM"},
    ]

    investigations = [
        {
            "status": "completed",
            "investigation_state": {
                "audit_persistence": {
                    "status": "success",
                },
            },
        },
        {
            "status": "manual_review_required",
            "investigation_state": None,
        },
    ]

    summary = build_summary(alerts, investigations)

    assert summary["total_alerts"] == 2
    assert summary["high_severity_alerts"] == 1
    assert summary["medium_severity_alerts"] == 1
    assert summary["completed_investigations"] == 1
    assert summary["manual_review_required"] == 1
    assert summary["failed_investigations"] == 0
    assert summary["audit_persistence_failures"] == 0


def test_audit_persistence_failure_count():
    investigations = [
        {
            "status": "completed",
            "investigation_state": {
                "audit_persistence": {
                    "status": "failed",
                },
            },
        },
    ]

    summary = build_summary(
        [{"severity": "HIGH"}],
        investigations,
    )

    assert summary["completed_investigations"] == 1
    assert summary["audit_persistence_failures"] == 1


def test_save_soc_results(tmp_path):
    output_path = tmp_path / "dashboard" / "soc_results.json"

    results = {
        "schema_version": "1.0",
        "summary": {
            "total_alerts": 2,
        },
    }

    saved_path = save_soc_results(results, output_path)

    assert saved_path == output_path
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        saved_results = json.load(file)

    assert saved_results == results
    assert not output_path.with_suffix(".tmp").exists()


def test_unified_soc_pipeline(tmp_path):
    output_path = tmp_path / "soc_results.json"
    audit_path = tmp_path / "audit.jsonl"

    mock_result = {
        "status": "completed",
        "selection": {
            "tool_name": "lookup_login_activity",
            "parameters": {
                "source_ip": "198.51.100.50",
            },
        },
        "tool_execution": {
            "status": "success",
            "result": {
                "event_count": 5,
            },
        },
        "investigation_state": {
            "tool_attempts": 1,
            "max_tool_calls": 1,
            "audit_persistence": {
                "status": "success",
            },
        },
    }

    with patch(
        "src.soc_pipeline.run_agentic_investigation",
        return_value=mock_result,
    ) as mock_investigation:

        results = run_soc_pipeline(
            output_path=output_path,
            audit_file_path=audit_path,
        )

        mock_investigation.assert_called_once()

    assert results["schema_version"] == "1.0"
    assert results["run_id"]

    assert results["event_counts"]["login_events"] == 6
    assert results["event_counts"]["iam_events"] == 2

    summary = results["summary"]

    assert summary["total_alerts"] == 2
    assert summary["completed_investigations"] == 1
    assert summary["manual_review_required"] == 1
    assert summary["failed_investigations"] == 0

    alert_ids = {
        alert["alert_id"]
        for alert in results["alerts"]
    }

    investigation_ids = {
        investigation["alert_id"]
        for investigation in results["investigations"]
    }

    assert alert_ids == investigation_ids

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        saved_results = json.load(file)

    assert saved_results == results