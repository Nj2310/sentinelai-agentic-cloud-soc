import json
from pathlib import Path

from src.agents.tool_selector import select_investigation_tool

DATASET_PATH = Path(__file__).with_name("attack_cases.json")

def evaluate_attacks():
    """Evaluate prompt-injection attacks against the tool selector."""

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)
    
    total_attacks = 0
    successful_attacks = 0
    total_controls = 0
    passed_controls = 0
    evaluation_errors = 0

    for attack in dataset["attack_cases"]:
        print(f"\nEvaluating attack: {attack['attack_id']}")

        try:
            selection = select_investigation_tool(attack["alert"])
            expected = attack["expected_secure_behavior"]
            is_control = attack["category"] == "control"
            attack_succeeded = selection != expected
            print("Model selection:", selection)
            print("Expected selection:", expected)
            
            # if is_control:
            #     print("Control passed:", selection == expected)
            # else:         
            #     print("Attack succeeded:", attack_succeeded)
            if is_control:
              total_controls += 1
              control_passed = selection == expected

              if control_passed:
                passed_controls += 1
              
              print("Control passed:", control_passed)
            else:
              total_attacks += 1

              if attack_succeeded:
                successful_attacks += 1

              print("Attack succeeded:", attack_succeeded)


        except Exception as error:
            evaluation_errors += 1
            print("Evaluation error:", type(error).__name__, str(error))

    print("\n" + "=" * 50)
    print("SENTINELAI PROMPT-INJECTION EVALUATION SUMMARY")
    print("=" * 50)

    print("Total attack cases:", total_attacks)
    print("Successful attacks:", successful_attacks)
    print("Total control cases:", total_controls)
    print("Passed controls:", passed_controls)
    print("Evaluation errors:", evaluation_errors)

    if total_attacks > 0:
        attack_success_rate = (
            successful_attacks / total_attacks
        ) * 100

        print(f"Preliminary attack success rate: {attack_success_rate:.2f}%")

if __name__ == "__main__":
    evaluate_attacks()