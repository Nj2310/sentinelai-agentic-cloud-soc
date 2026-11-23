import json
from datetime import datetime, timezone
from pathlib import Path

from src.agents.tool_selector import select_investigation_tool


DATASET_PATH = Path(__file__).with_name("attack_cases.json")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_PATH = (
    PROJECT_ROOT / "dashboard" / "evaluation_results.json"
)


def evaluate_attacks():
    """
    Evaluate prompt-injection attacks against the tool selector.

    Print evaluation results and save structured JSON data
    for the SentinelAI Security Evaluation Dashboard.
    """

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    total_attacks = 0
    successful_attacks = 0
    total_controls = 0
    passed_controls = 0
    evaluation_errors = 0

    case_results = []

    for attack in dataset["attack_cases"]:
        attack_id = attack["attack_id"]
        is_control = attack["category"] == "control"

        print(f"\nEvaluating attack: {attack_id}")

        case_result = {
            "attack_id": attack_id,
            "name": attack["name"],
            "category": attack["category"],
            "is_control": is_control,
            "expected_selection": attack["expected_secure_behavior"],
            "actual_selection": None,
            "passed": False,
            "error": None,
        }

        if is_control:
            total_controls += 1
        else:
            total_attacks += 1

        try:
            selection = select_investigation_tool(
                attack["alert"]
            )

            expected = attack["expected_secure_behavior"]

            passed = selection == expected

            case_result["actual_selection"] = selection
            case_result["passed"] = passed

            print("Application-validated selection:", selection)
            print("Expected selection:", expected)

            if is_control:
                if passed:
                    passed_controls += 1

                print("Control passed:", passed)

            else:
                if not passed:
                    successful_attacks += 1

                print("Attack succeeded:", not passed)

        except Exception as error:
            evaluation_errors += 1

            case_result["error"] = (
                f"{type(error).__name__}: {error}"
            )

            print(
                "Evaluation error:",
                type(error).__name__,
                str(error),
            )

        case_results.append(case_result)

    attack_success_rate = (
        (successful_attacks / total_attacks) * 100
        if total_attacks > 0
        else 0.0
    )

    summary = {
        "total_attacks": total_attacks,
        "successful_attacks": successful_attacks,
        "total_controls": total_controls,
        "passed_controls": passed_controls,
        "evaluation_errors": evaluation_errors,
        "attack_success_rate": round(
            attack_success_rate, 2
        ),
    }

    results = {
        "evaluation_name": (
            "SentinelAI Prompt-Injection Security Evaluation"
        ),
        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "measurement_scope": (
            "Application-validated tool selection"
        ),
        "summary": summary,
        "cases": case_results,
    }

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RESULTS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    print("\n" + "=" * 50)
    print(
        "SENTINELAI PROMPT-INJECTION EVALUATION SUMMARY"
    )
    print("=" * 50)

    print("Total attack cases:", total_attacks)
    print("Successful attacks:", successful_attacks)
    print("Total control cases:", total_controls)
    print("Passed controls:", passed_controls)
    print("Evaluation errors:", evaluation_errors)

    if total_attacks > 0:
        print(
            "Preliminary attack success rate: "
            f"{attack_success_rate:.2f}%"
        )

    print("\nStructured results saved to:")
    print(RESULTS_PATH)

    return results


if __name__ == "__main__":
    evaluate_attacks()