import csv
from pathlib import Path
from detector import detect_brute_force

# Locate the project root and authentication dataset
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "data" / "authentication_logs.csv"


def load_ground_truth():
    """Load labeled authentication events and group labels by source IP."""

    ip_labels = {}

    with open(LOG_FILE, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ip = row["source_ip"].strip()
            label = row["ground_truth"].strip().lower()

            if label not in {"benign", "malicious"}:
                raise ValueError(f"Unexpected ground_truth label: {label}")

            if ip in ip_labels and ip_labels[ip] != label:
                raise ValueError(f"Conflicting labels for source IP: {ip}")

            ip_labels[ip] = label

    return ip_labels

if __name__ == "__main__":
    ground_truth = load_ground_truth()

    predicted_ips = detect_brute_force()

    # Evaluate detector predictions against ground truth
    # tp = True Positives, fp = False Positives, tn = True Negatives, fn = False Negatives
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for ip, actual_label in ground_truth.items():
        predicted_malicious = ip in predicted_ips
        actual_malicious = actual_label == "malicious"

        if predicted_malicious and actual_malicious:
            tp += 1
        elif predicted_malicious and not actual_malicious:
            fp += 1
        elif not predicted_malicious and actual_malicious:
            fn += 1
        else:
            tn += 1

    print("\nSentinelAI - Confusion Matrix")
    print("=" * 45)
    print(f"True Positives (TP):  {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"True Negatives (TN):  {tn}")
    print(f"False Negatives (FN): {fn}")

    # Calculate evaluation metrics
    total = tp + fp + tn + fn

    accuracy = (tp + tn) / total if total > 0 else 0
    # Calculate the False Positive Rate that measure how frequently benign activity is incorrectly flagged.
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    print(f"False Positive Rate: {false_positive_rate:.2%}")
    
    print("\nSentinelAI - Detection Performance Metrics")
    print("=" * 45)
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1 Score:  {f1_score:.2%}")

    print("\nSentinelAI - Detector Prediction Verification")
    print("=" * 45)
    print(f"Predicted suspicious IPs: {predicted_ips}")
    print(f"Prediction data type: {type(predicted_ips).__name__}")

    print("SentinelAI - Ground Truth Verification")
    print("=" * 45)

    for ip, label in sorted(ground_truth.items()):
        print(f"Source IP: {ip} | Ground Truth: {label}")

    print("=" * 45)
    print(f"Total unique source IPs: {len(ground_truth)}")