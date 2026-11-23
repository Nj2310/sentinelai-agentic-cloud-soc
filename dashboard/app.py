import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


RESULTS_PATH = Path(__file__).with_name(
    "evaluation_results.json"
)

st.set_page_config(
    page_title="SentinelAI | Security Evaluation",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data
def load_results(path, modified_time):
    """Load a saved security evaluation snapshot."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


st.title("🛡️ SentinelAI")
st.subheader("Agentic AI Cloud SOC — Security Evaluation Dashboard")

st.caption(
    "Prompt-injection evaluation of application-validated "
    "investigation tool selections."
)

if not RESULTS_PATH.exists():
    st.error(
        "Evaluation results not found. Run: "
        "python -m tests.prompt_injection.evaluate_attacks"
    )
    st.stop()

try:
    results = load_results(
        str(RESULTS_PATH),
        RESULTS_PATH.stat().st_mtime_ns,
    )
except (OSError, json.JSONDecodeError) as error:
    st.error(f"Unable to load evaluation results: {error}")
    st.stop()

summary = results["summary"]
cases = results["cases"]

evaluated_at = datetime.fromisoformat(
    results["evaluated_at"]
)

st.info(
    f"Evaluation snapshot: "
    f"{evaluated_at.strftime('%Y-%m-%d %H:%M:%S UTC')} "
    f"| Scope: {results['measurement_scope']}"
)

st.divider()

st.header("Security Evaluation Overview")

metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    "Attack Success Rate",
    f"{summary['attack_success_rate']:.1f}%",
)

metric_2.metric(
    "Attacks Blocked",
    (
        f"{summary['total_attacks'] - summary['successful_attacks']}"
        f"/{summary['total_attacks']}"
    ),
)

metric_3.metric(
    "Controls Passed",
    (
        f"{summary['passed_controls']}"
        f"/{summary['total_controls']}"
    ),
)

metric_4.metric(
    "Evaluation Errors",
    summary["evaluation_errors"],
)

st.caption(
    "Attack outcomes measure final application-validated selections, "
    "not raw LLM responses. Results are based on a small synthetic dataset."
)

if summary["evaluation_errors"]:
    st.warning(
        "Some evaluations failed with errors. The attack success "
        "rate does not include those failures."
    )

st.divider()

st.header("Attack Outcome Breakdown")

attack_cases = [
    case for case in cases
    if not case["is_control"]
]

successful_attacks = sum(
    case["passed"] is False and case["error"] is None
    for case in attack_cases
)

blocked_attacks = sum(
    case["passed"] is True and case["error"] is None
    for case in attack_cases
)

errored_attacks = sum(
    case["error"] is not None
    for case in attack_cases
)

outcome_data = pd.DataFrame(
    {
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
    }
).set_index("Outcome")

st.bar_chart(outcome_data)

st.divider()

st.header("Attack-by-Attack Results")

table_rows = []

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

    actual = case["actual_selection"] or {}
    expected = case["expected_selection"]

    table_rows.append(
        {
            "Case ID": case["attack_id"],
            "Name": case["name"],
            "Category": case["category"],
            "Status": status,
            "Expected Tool": expected.get("tool_name"),
            "Actual Tool": actual.get("tool_name"),
            "Source IP": (
                expected.get("parameters", {})
                .get("source_ip", "")
            ),
        }
    )

results_df = pd.DataFrame(table_rows)

st.dataframe(
    results_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.header("Detailed Evaluation Evidence")

selected_case_id = st.selectbox(
    "Select an evaluation case",
    options=[case["attack_id"] for case in cases],
)

selected_case = next(
    case for case in cases
    if case["attack_id"] == selected_case_id
)

detail_left, detail_right = st.columns(2)

with detail_left:
    st.markdown("**Expected secure selection**")
    st.json(selected_case["expected_selection"])

with detail_right:
    st.markdown("**Actual application selection**")
    st.json(selected_case["actual_selection"])

if selected_case["error"]:
    st.error(selected_case["error"])
elif selected_case["passed"]:
    st.success("Application selection matched expected behavior.")
else:
    st.error("Application selection did not match expected behavior.")

st.divider()

st.header("Evaluation Scope and Limitations")

st.markdown(
    """
    - Results come from a saved evaluation snapshot, not a live SOC.
    - The dataset contains synthetic prompt-injection scenarios.
    - The evaluator checks final application-validated tool selections.
    - Raw model responses are not stored in this dataset.
    - Evaluation exceptions are reported separately.
    - A zero-percent observed attack success rate does not prove
      comprehensive resistance to prompt injection.
    """
)

st.caption(
    "SentinelAI | Local-first Agentic AI Cloud Security Operations"
)