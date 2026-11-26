import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.agents.agentic_workflow import run_agentic_investigation
from src.cloudtrail_parser import parse_cloudtrail_logs
from src.detector import detect_brute_force
from src.iam_parser import parse_iam_events
from src.iam_detector import detect_suspicious_iam_activity


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOC_RESULTS_PATH = (
    PROJECT_ROOT / "dashboard" / "soc_results.json"
)

AUDIT_LOG_PATH = (
    PROJECT_ROOT / "reports" / "investigation_audit.jsonl"
)


def normalize_iam_alert(alert: dict) -> dict:
    """Convert an IAM finding into a standardized SOC alert."""

    return {
        "alert_id": str(uuid4()),
        "alert_type": alert["alert_type"],
        "severity": alert["severity"].upper(),
        "source_ip": alert.get("source_ip"),
        "detection_time": alert.get("timestamp"),
        "actor": alert.get("actor"),
        "target_user": alert.get("target_user"),
        "reason": alert.get("reason"),
        "mitre_attack": "T1098.001",
        "recommended_action": (
            "Review access key creation and verify authorization."
        ),
        "status": "needs_investigation",
    }


def investigate_alert(alert: dict, audit_file_path) -> dict:
    """Route supported alerts to controlled investigations."""

    if alert["alert_type"] != "BRUTE_FORCE":
        return {
            "alert_id": alert["alert_id"],
            "status": "manual_review_required",
            "reason": (
                "No approved automated investigation "
                "tool is available for this alert type."
            ),
            "selection": None,
            "tool_execution": None,
            "investigation_state": None,
        }

    try:
        result = run_agentic_investigation(
            alert=alert,
            audit_file_path=audit_file_path,
        )

        return {
            "alert_id": alert["alert_id"],
            "status": result["status"],
            "selection": result.get("selection"),
            "tool_execution": result.get("tool_execution"),
            "investigation_state": result.get(
                "investigation_state"
            ),
        }

    except Exception as error:
        return {
            "alert_id": alert["alert_id"],
            "status": "failed",
            "error_type": type(error).__name__,
            "selection": None,
            "tool_execution": None,
            "investigation_state": None,
        }


def build_summary(alerts: list, investigations: list) -> dict:
    """Calculate metrics from the current SOC run."""

    return {
        "total_alerts": len(alerts),

        "high_severity_alerts": sum(
            alert["severity"] == "HIGH"
            for alert in alerts
        ),

        "medium_severity_alerts": sum(
            alert["severity"] == "MEDIUM"
            for alert in alerts
        ),

        "completed_investigations": sum(
            result["status"] == "completed"
            for result in investigations
        ),

        "failed_investigations": sum(
            result["status"] == "failed"
            for result in investigations
        ),

        "no_tool_selected": sum(
            result["status"] == "no_tool_selected"
            for result in investigations
        ),

        "manual_review_required": sum(
            result["status"] == "manual_review_required"
            for result in investigations
        ),

        "audit_persistence_failures": sum(
            (
                (result.get("investigation_state") or {})
                .get("audit_persistence", {})
                .get("status") == "failed"
            )
            for result in investigations
        ),
    }


def save_soc_results(results: dict, output_path) -> Path:
    """Write a structured SOC snapshot for the dashboard."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(results, file, indent=4)

    temporary_path.replace(path)

    return path


def run_soc_pipeline(
    output_path=SOC_RESULTS_PATH,
    audit_file_path=AUDIT_LOG_PATH,
) -> dict:
    """Run detection, investigation, and SOC result export."""

    run_id = str(uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    # Phase 1: Parse authentication events.
    login_events = parse_cloudtrail_logs()

    # Phase 2: Detect brute-force activity.
    brute_force_alerts = detect_brute_force(
        events=login_events,
        save_alerts=False,
        return_alerts=True,
    )

    # Phase 3: Parse and detect IAM activity.
    iam_events = parse_iam_events()

    iam_findings = detect_suspicious_iam_activity(
        iam_events
    )

    iam_alerts = [
        normalize_iam_alert(alert)
        for alert in iam_findings
    ]

    # Phase 4: Combine current-run alerts.
    alerts = brute_force_alerts + iam_alerts

    # Phase 5: Route alerts for investigation.
    investigations = []

    for alert in alerts:
        investigation = investigate_alert(
            alert,
            audit_file_path,
        )

        investigations.append(investigation)

    # Phase 6: Build the SOC snapshot.
    results = {
        "schema_version": "1.0",
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "data_source": "Synthetic AWS CloudTrail logs",

        "event_counts": {
            "login_events": len(login_events),
            "iam_events": len(iam_events),
        },

        "summary": build_summary(
            alerts,
            investigations,
        ),

        "alerts": alerts,
        "investigations": investigations,
    }

    # Phase 7: Export dashboard results.
    saved_path = save_soc_results(
        results,
        output_path,
    )

    print("\n" + "=" * 55)
    print("SentinelAI - Unified SOC Pipeline")
    print("=" * 55)
    print(json.dumps(results["summary"], indent=4))
    print(f"\nSOC results saved: {saved_path}")

    return results


if __name__ == "__main__":
    run_soc_pipeline()