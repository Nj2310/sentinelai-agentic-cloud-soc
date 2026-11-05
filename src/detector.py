import csv
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from alert_writer import save_alert

# Locate our synthetic authentication dataset
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "data" / "authentication_logs.csv"

# Detection configuration
FAILED_LOGIN_THRESHOLD = 5
TIME_WINDOW = timedelta(minutes=5)


def detect_brute_force():
    failed_attempts = defaultdict(deque)
    alerted_ips = set()

    with open(LOG_FILE, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        # Process authentication events chronologically
        events = sorted(
            reader,
            key=lambda row: datetime.strptime(
                row["timestamp"], "%Y-%m-%d %H:%M:%S"
            ),
        )

    print("=" * 55)
    print("SentinelAI - Brute-Force Detection Engine")
    print("=" * 55)

    for event in events:
        ip = event["source_ip"]
        status = event["status"].strip().lower()
        timestamp = datetime.strptime(
            event["timestamp"], "%Y-%m-%d %H:%M:%S"
        )

        # Track failed attempts for each source IP
        if status == "failure":
            attempts = failed_attempts[ip]
            attempts.append(timestamp)

            # Remove attempts outside the five-minute window
            while attempts and timestamp - attempts[0] > TIME_WINDOW:
                attempts.popleft()

            # Generate one alert per IP
            if len(attempts) >= FAILED_LOGIN_THRESHOLD and ip not in alerted_ips:
                alerted_ips.add(ip)

                print("\n[HIGH] Potential Brute-Force Attack Detected")
                print(f"Source IP: {ip}")
                print(f"Failed Attempts: {len(attempts)}")
                print(f"Detection Time: {timestamp}")
                print("MITRE ATT&CK: T1110 - Brute Force")
                print("Recommended Action: Investigate authentication activity.")
                save_alert(ip, len(attempts), timestamp.isoformat())

    if not alerted_ips:
        print("No brute-force activity detected.")

    print("\nDetection completed.")
    print(f"Total suspicious source IPs: {len(alerted_ips)}")


if __name__ == "__main__":
    detect_brute_force()