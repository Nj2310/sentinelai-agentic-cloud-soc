
import csv
from pathlib import Path

# Locate the CSV file in the project's data folder
project_root = Path(__file__).resolve().parent.parent
log_file = project_root / "data" / "authentication_logs.csv"

print("SentinelAI - Authentication Log Reader")
print("=" * 45)

with open(log_file, mode="r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        print(
            f"{row['timestamp']} | "
            f"User: {row['username']} | "
            f"IP: {row['source_ip']} | "
            f"Status: {row['status']}"
        )

print("=" * 45)
print("Log reading completed successfully.")
