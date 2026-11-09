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


def detect_brute_force(log_file=LOG_FILE, save_alerts=True, events=None):
    failed_attempts = defaultdict(deque)
    alerted_ips = set()

    
    # with open(log_file, mode="r", encoding="utf-8-sig", newline="") as file:
    #     reader = csv.DictReader(file)

    #     # Validate timestamps before processing events
    #     valid_events = []

    #     for row in reader:
    #         try:
    #             timestamp = datetime.strptime(
    #                 row["timestamp"], "%Y-%m-%d %H:%M:%S"
    #             )

    #             valid_events.append((timestamp, row))

    #         except (ValueError, KeyError, TypeError):
    #             print(
    #                 f"[WARNING] Skipping event with invalid timestamp: "
    #                 f"{row.get('timestamp')}"
    #             )

    #     # Process valid authentication events chronologically
    #     events = [
    #         row
    #         for timestamp, row in sorted(
    #             valid_events,
    #             key=lambda item: item[0]
    #         )
    #     ]

    
    # Use supplied events or load authentication events from CSV
    if events is None:
        with open(log_file, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            raw_events = list(reader)
    else:
        raw_events = events

    # Validate and sort authentication events
    valid_events = []

    for row in raw_events:
        try:
            timestamp = datetime.strptime(
                row["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
            valid_events.append((timestamp, row))

        except (ValueError, KeyError, TypeError):
            print(
                f"[WARNING] Skipping event with invalid timestamp: "
                f"{row.get('timestamp')}"
            )

    events = [
        row
        for timestamp, row in sorted(
            valid_events,
            key=lambda item: item[0]
        )
    ]

    print("=" * 55)
    print("SentinelAI - Brute-Force Detection Engine")
    print("=" * 55)

    for event in events:
        # ip = event["source_ip"]
        # status = event["status"].strip().lower()
        ip = (event.get("source_ip") or "").strip()

        # Skip events with missing source IP addresses
        if not ip:
            print("[WARNING] Skipping event with missing source IP.")
            continue
        
        status = event["status"].strip().lower()
        timestamp = datetime.strptime(
            event["timestamp"], "%Y-%m-%d %H:%M:%S"
        )

        # Track failed attempts for each source IP
        if status in {"failure", "failed"}:
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
                
                if save_alerts:
                    save_alert(ip, len(attempts), timestamp.isoformat())

    if not alerted_ips:
        print("No brute-force activity detected.")

    print("\nDetection completed.")
    print(f"Total suspicious source IPs: {len(alerted_ips)}")
    
    return alerted_ips


if __name__ == "__main__":
    # Use the original authentication dataset
    detect_brute_force()

    # Use the new benign login test dataset
    detect_brute_force("data/benign_login_test.csv")