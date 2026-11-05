import json
from pathlib import Path
from datetime import datetime, timezone

# SentinelAI project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = PROJECT_ROOT / "alerts"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure the reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Create the function to read security alerts 
def load_alerts():
    """Load all security alerts from the alerts directory."""

    alerts = []

    for alert_file in sorted(ALERTS_DIR.glob("*.json")):
        with open(alert_file, "r", encoding="utf-8") as file:
            alert_data = json.load(file)
            alerts.append(alert_data)

    return alerts

# Building the SOC Investigation Report Generator
def generate_report():
    """Generate a SOC investigation report from saved alerts."""

    alerts = load_alerts()

    high_alerts = sum(
    1 for alert in alerts
    if alert.get("severity", "").upper() == "HIGH"
    )

    unique_ips = {
    alert.get("source_ip")
    for alert in alerts
    if alert.get("source_ip")
    }

    if high_alerts > 0:
        risk_level = "HIGH"
        risk_description = (
            "High-severity authentication alerts were detected. "
            "Prompt investigation is recommended."
            )
    elif alerts:
        risk_level = "MEDIUM"
        risk_description = (
            "Security alerts were detected. "
            "Review the activity to determine its impact."
            )
    else:
        risk_level = "LOW"
        risk_description = "No security alerts were found."

    # report_lines = [
    # "SENTINELAI - SOC INVESTIGATION REPORT",
    # "=" * 50,
    # f"Generated At: {datetime.now(timezone.utc).isoformat()}",
    # f"Total Security Alerts: {len(alerts)}",
    # "=" * 50,
    # ""
    # ]

    report_lines = [
        "SENTINELAI - SOC INVESTIGATION REPORT",
    "=" * 50,
    f"Generated At: {datetime.now(timezone.utc).isoformat()}",
    f"Total Security Alerts: {len(alerts)}",
    "=" * 50,
    "",
    "EXECUTIVE SUMMARY",
    "-" * 50,
    f"Total Alerts Analyzed: {len(alerts)}",
    f"High Severity Alerts: {high_alerts}",
    f"Unique Source IPs: {len(unique_ips)}",
    "",
    "Summary:",
    (
        "The SentinelAI detection engine identified "
        f"{len(alerts)} security alert(s), including "
        f"{high_alerts} high-severity alert(s)."
    ),
    # "Potential brute-force activity requires investigation.",
    # "",
    # "=" * 50,
    # ""
    "Potential brute-force activity requires investigation."
    if alerts else "No security alerts were detected.",
    "",
    "RISK ASSESSMENT",
    "-" * 50,
    f"Overall Risk Level: {risk_level}",
    f"Risk Description: {risk_description}",
    "",
    "RECOMMENDED SOC RESPONSE ACTIONS",
    "-" * 50,
    "1. Review authentication logs for suspicious login attempts.",
    "2. Investigate source IP addresses associated with alerts.",
    "3. Check whether affected accounts were accessed successfully.",
    "4. Review account lockout and MFA protections.",
    "5. Escalate confirmed suspicious activity according to the incident response plan.",
    "",
    "=" * 50,
    ""
    ]

    for index, alert in enumerate(alerts, start=1):
        report_lines.extend([
            f"ALERT #{index}",
            "-" * 50,
            f"Alert ID: {alert.get('alert_id', 'N/A')}",
            f"Alert Type: {alert.get('alert_type', 'N/A')}",
            f"Severity: {alert.get('severity', 'N/A')}",
            f"Source IP: {alert.get('source_ip', 'N/A')}",
            f"Failed Attempts: {alert.get('failed_attempts', 'N/A')}",
            f"Detection Time: {alert.get('detection_time', 'N/A')}",
            f"MITRE ATT&CK: {alert.get('mitre_attack', 'N/A')}",
            f"Recommended Action: {alert.get('recommended_action', 'N/A')}",
            ""
        ])

    # report_lines.append("=" * 50)
    # report_lines.append("END OF INVESTIGATION REPORT")
    report_lines.extend([
        "",
        "INVESTIGATION CONCLUSION",
        "-" * 50,
        (
            f"SentinelAI analyzed {len(alerts)} security alert(s) "
            f"from {len(unique_ips)} unique source IP(s)."
        ),
        (
            f"The overall risk level was classified as {risk_level} "
            "based on the severity of detected alerts."
        ),
        (
            "The findings indicate potentially suspicious "
            "authentication activity that requires further investigation."
            if alerts else
            "No security alerts were identified in the analyzed dataset."
        ),
        "",
        "Investigation Status: Pending Analyst Review" if alerts
        else "Investigation Status: No Alerts Identified",
        "",
        "=" * 50,
        "END OF INVESTIGATION REPORT"
    ])

    report_content = "\n".join(report_lines)

    report_filename = (
        f"soc_investigation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
    )

    report_path = REPORTS_DIR / report_filename

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report_content)

    print(f"SOC investigation report saved: {report_path}")

    return report_path


if __name__ == "__main__":
    generate_report()
