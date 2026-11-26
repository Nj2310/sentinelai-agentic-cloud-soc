
import json
from pathlib import Path

import pandas as pd
import streamlit as st


SOC_RESULTS_PATH = Path(__file__).with_name(
    "soc_results.json"
)

EVALUATION_RESULTS_PATH = Path(__file__).with_name(
    "evaluation_results.json"
)


st.set_page_config(
    page_title="SentinelAI | Cloud SOC",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data
def load_results(path, modified_time):
    """Load a saved JSON snapshot."""

    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def read_snapshot(path, generation_command):
    """Safely load a dashboard snapshot."""

    if not path.exists():
        st.warning("Results snapshot not found.")
        st.code(generation_command, language="powershell")
        return None

    try:
        return load_results(
            str(path),
            path.stat().st_mtime_ns,
        )

    except (OSError, json.JSONDecodeError):
        st.error("Unable to read the results snapshot.")
        return None


def render_soc_dashboard():
    """Display saved SOC results without executing tools."""

    st.header("SOC Operations Overview")

    results = read_snapshot(
        SOC_RESULTS_PATH,
        "python -m src.main",
    )

    if results is None:
        return

    summary = results["summary"]
    alerts = results["alerts"]
    investigations = results["investigations"]
    event_counts = results["event_counts"]

    st.caption(
        f"Data source: {results['data_source']}"
    )

    st.info(
        f"Run completed: {results['completed_at']}"
    )

    st.caption(f"Run ID: {results['run_id']}")

    total_events = (
        event_counts["login_events"]
        + event_counts["iam_events"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Events Processed", total_events)
    col2.metric("Security Alerts", summary["total_alerts"])

    col3.metric(
        "Completed Investigations",
        summary["completed_investigations"],
    )

    col4.metric(
        "Manual Review Required",
        summary["manual_review_required"],
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "High Severity",
        summary["high_severity_alerts"],
    )

    col6.metric(
        "Medium Severity",
        summary["medium_severity_alerts"],
    )

    col7.metric(
        "Failed Investigations",
        summary["failed_investigations"],
    )

    col8.metric(
        "Audit Persistence Failures",
        summary["audit_persistence_failures"],
    )

    if summary["audit_persistence_failures"]:
        st.warning(
            "One or more investigations reported "
            "audit persistence failures."
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Alert Severity Distribution")

        severity_data = pd.DataFrame({
            "Severity": ["HIGH", "MEDIUM"],
            "Count": [
                summary["high_severity_alerts"],
                summary["medium_severity_alerts"],
            ],
        }).set_index("Severity")

        st.bar_chart(severity_data)

    with right:
        st.subheader("Investigation Outcomes")

        outcome_data = pd.DataFrame({
            "Outcome": [
                "Completed",
                "Manual Review",
                "Failed",
                "No Tool Selected",
            ],
            "Count": [
                summary["completed_investigations"],
                summary["manual_review_required"],
                summary["failed_investigations"],
                summary["no_tool_selected"],
            ],
        }).set_index("Outcome")

        st.bar_chart(outcome_data)

    st.divider()
    st.header("Security Alert Queue")

    investigation_map = {
        item["alert_id"]: item
        for item in investigations
    }

    if not alerts:
        st.info("No alerts were generated in this run.")
        return

    severity_filter = st.multiselect(
        "Filter by severity",
        options=sorted({
            alert["severity"] for alert in alerts
        }),
        default=sorted({
            alert["severity"] for alert in alerts
        }),
    )

    filtered_alerts = [
        alert for alert in alerts
        if alert["severity"] in severity_filter
    ]

    if not filtered_alerts:
        st.info("No alerts match the selected filters.")
        return

    alert_rows = []

    for alert in filtered_alerts:
        investigation = investigation_map.get(
            alert["alert_id"], {}
        )

        alert_rows.append({
            "Alert Type": alert["alert_type"],
            "Severity": alert["severity"],
            "Source IP": alert.get("source_ip"),
            "Detection Time": alert.get("detection_time"),
            "MITRE ATT&CK": alert.get("mitre_attack"),
            "Investigation Status": investigation.get(
                "status", "not_available"
            ),
        })

    st.dataframe(
        pd.DataFrame(alert_rows),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()
    st.header("Investigation Evidence")

    alert_map = {
        alert["alert_id"]: alert
        for alert in filtered_alerts
    }

    selected_alert_id = st.selectbox(
        "Select an alert",
        options=list(alert_map),
        format_func=lambda alert_id: (
            f"{alert_map[alert_id]['alert_type']} | "
            f"{alert_map[alert_id].get('source_ip')} | "
            f"{alert_id[:8]}"
        ),
    )

    selected_alert = alert_map[selected_alert_id]

    investigation = investigation_map.get(
        selected_alert_id
    )

    with st.expander("Original Alert Details", expanded=True):
        st.json(selected_alert)

    if investigation is None:
        st.warning("Investigation record not available.")
        return

    status = investigation["status"]

    if status == "completed":
        st.success("Automated investigation completed.")

    elif status == "manual_review_required":
        st.warning("Manual security review required.")

    elif status == "failed":
        st.error("Automated investigation failed.")

    else:
        st.info(f"Investigation status: {status}")

    if investigation.get("reason"):
        st.write(investigation["reason"])

    if investigation.get("error_type"):
        st.caption(
            f"Error type: {investigation['error_type']}"
        )

    selection = investigation.get("selection")

    if selection is not None:
        st.subheader("Application-Validated Tool Selection")
        st.json(selection)

    execution = investigation.get("tool_execution")

    if execution is not None:
        st.subheader("Tool Execution Evidence")

        evidence = execution.get("result") or {}

        st.metric(
            "Matching Events",
            evidence.get("event_count", 0),
        )

        matching_events = evidence.get(
            "matching_events", []
        )

        if matching_events:
            st.dataframe(
                pd.DataFrame(matching_events),
                hide_index=True,
                use_container_width=True,
            )

        with st.expander("Full Tool Execution Record"):
            st.json(execution)

    state = investigation.get("investigation_state")

    if state is not None:
        st.divider()
        st.subheader("Investigation Security Controls")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Tool Attempts",
            (
                f"{state['tool_attempts']}"
                f"/{state['max_tool_calls']}"
            ),
        )

        c2.metric(
            "Successful Tool Executions",
            state["tool_calls_used"],
        )

        persistence = state.get(
            "audit_persistence", {}
        )

        c3.metric(
            "Audit Persistence",
            persistence.get(
                "status", "not_requested"
            ).upper(),
        )

        st.caption(
            f"Investigation ID: "
            f"{state['investigation_id']}"
        )

        st.subheader("Investigation Audit Trail")

        audit_log = state.get("audit_log", [])

        if audit_log:
            st.dataframe(
                pd.DataFrame(audit_log),
                hide_index=True,
                use_container_width=True,
            )

        else:
            st.info("No audit events available.")

        st.caption(
            "Audit events are displayed from the saved "
            "SOC snapshot. Persistence status is reported "
            "by the investigation workflow."
        )

    st.divider()

    st.subheader("SOC Scope and Limitations")

    st.markdown("""
    - Results are based on synthetic AWS CloudTrail logs.
    - The dashboard displays saved investigation snapshots.
    - No LLM calls or tools are executed by the dashboard.
    - Automated investigation supports brute-force alerts.
    - IAM findings require manual security review.
    - Investigation completion does not imply remediation.
    - Local audit storage is not tamper-proof.
    """)


def render_evaluation_dashboard():
    """Display saved prompt-injection evaluation results."""

    st.header("AI Security Evaluation")

    results = read_snapshot(
        EVALUATION_RESULTS_PATH,
        "python -m tests.prompt_injection.evaluate_attacks",
    )

    if results is None:
        return

    summary = results["summary"]
    cases = results["cases"]

    st.info(
        f"Evaluation snapshot: {results['evaluated_at']}"
    )

    st.caption(
        f"Scope: {results['measurement_scope']}"
    )

    attack_cases = [
        case for case in cases
        if not case["is_control"]
    ]

    successful_attacks = sum(
        case["passed"] is False
        and case["error"] is None
        for case in attack_cases
    )

    blocked_attacks = sum(
        case["passed"] is True
        and case["error"] is None
        for case in attack_cases
    )

    errored_attacks = sum(
        case["error"] is not None
        for case in attack_cases
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Attack Success Rate",
        f"{summary['attack_success_rate']:.1f}%",
    )

    col2.metric(
        "Attacks Blocked",
        f"{blocked_attacks}/{len(attack_cases)}",
    )

    col3.metric(
        "Controls Passed",
        (
            f"{summary['passed_controls']}"
            f"/{summary['total_controls']}"
        ),
    )

    col4.metric(
        "Evaluation Errors",
        summary["evaluation_errors"],
    )

    if summary["evaluation_errors"]:
        st.warning(
            "Some evaluations encountered errors. "
            "Errors are not counted as blocked attacks."
        )

    st.divider()
    st.subheader("Attack Outcome Breakdown")

    outcome_data = pd.DataFrame({
        "Outcome": [
            "Blocked",
            "Successful",
            "Evaluation Error",
        ],
        "Count": [
            blocked_attacks,
            successful_attacks,
            errored_attacks,
        ],
    }).set_index("Outcome")

    st.bar_chart(outcome_data)

    st.divider()
    st.subheader("Attack-by-Attack Results")

    rows = []

    for case in cases:
        if case["error"] is not None:
            status = "ERROR"

        elif case["is_control"]:
            status = (
                "CONTROL PASSED"
                if case["passed"]
                else "CONTROL FAILED"
            )

        else:
            status = (
                "ATTACK BLOCKED"
                if case["passed"]
                else "ATTACK SUCCEEDED"
            )

        expected = case["expected_selection"]
        actual = case["actual_selection"] or {}

        rows.append({
            "Case ID": case["attack_id"],
            "Name": case["name"],
            "Category": case["category"],
            "Status": status,
            "Expected Tool": expected.get("tool_name"),
            "Actual Tool": actual.get("tool_name"),
            "Source IP": expected.get(
                "parameters", {}
            ).get("source_ip", ""),
        })

    if not cases:
        st.info("No evaluation cases available.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()
    st.subheader("Detailed Evaluation Evidence")

    case_map = {
        case["attack_id"]: case
        for case in cases
    }

    selected_case_id = st.selectbox(
        "Select an evaluation case",
        options=list(case_map),
    )

    selected_case = case_map[selected_case_id]

    left, right = st.columns(2)

    with left:
        st.markdown("**Expected secure selection**")
        st.json(selected_case["expected_selection"])

    with right:
        st.markdown("**Actual application selection**")
        st.json(selected_case["actual_selection"])

    if selected_case["error"] is not None:
        st.error("Evaluation encountered an error.")

    elif selected_case["passed"]:
        st.success(
            "Application selection matched expected behavior."
        )

    else:
        st.error(
            "Application selection did not match "
            "expected behavior."
        )

    st.divider()
    st.subheader("Evaluation Scope and Limitations")

    st.markdown("""
    - Results come from a saved evaluation snapshot.
    - The dataset contains synthetic prompt-injection cases.
    - Outcomes measure application-validated tool selections.
    - Raw LLM responses are not stored in the dataset.
    - Evaluation errors are reported separately.
    - Zero observed attack success does not prove
      comprehensive resistance to prompt injection.
    """)


st.title("🛡️ SentinelAI")

st.subheader(
    "Agentic AI Cloud Security Operations Platform"
)

st.caption(
    "Local-first security monitoring, controlled AI "
    "investigation, and AI security evaluation."
)

soc_tab, evaluation_tab = st.tabs([
    "SOC Operations",
    "AI Security Evaluation",
])

with soc_tab:
    render_soc_dashboard()

with evaluation_tab:
    render_evaluation_dashboard()

st.divider()

st.caption(
    "SentinelAI | Read-only Security Operations Dashboard"
)