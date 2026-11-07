# def test_basic_assertion():
#     """Verify that Pytest can execute a simple test."""

#     expected_alerts = 0
#     actual_alerts = 0

#     assert actual_alerts == expected_alerts

import sys
from pathlib import Path

# Locate the project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
SRC_DIR = PROJECT_ROOT / "src"

# Allow Python to import the detection engine
sys.path.insert(0, str(SRC_DIR))

from detector import detect_brute_force


def test_benign_login_no_alert():
    """Verify that benign login activity does not trigger an alert."""

    test_file = PROJECT_ROOT / "data" / "benign_login_test.csv"

    detected_ips = detect_brute_force(test_file)

    assert detected_ips == set()

def test_malicious_brute_force_detected():
    """Verify that five failed logins trigger brute-force detection."""

    test_file = PROJECT_ROOT / "data" / "malicious_login_test.csv"

    detected_ips = detect_brute_force(test_file)

    expected_ips = {"198.51.100.50"}

    assert detected_ips == expected_ips

def test_four_failed_logins_no_alert():
    """Verify that four failed logins do not trigger an alert."""

    test_file = PROJECT_ROOT / "data" / "threshold_boundary_test.csv"

    detected_ips = detect_brute_force(test_file)

    assert detected_ips == set()

def test_failed_logins_outside_time_window():
    """Verify that failed logins spread over 20 minutes do not trigger an alert."""

    test_file = PROJECT_ROOT / "data" / "time_window_test.csv"

    detected_ips = detect_brute_force(test_file)

    assert detected_ips == set()

def test_exact_five_minute_boundary():
    """Verify detection when five failures span exactly five minutes."""

    test_file = PROJECT_ROOT / "data" / "exact_time_boundary_test.csv"

    detected_ips = detect_brute_force(test_file)

    expected_ips = {"198.51.100.80"}

    assert detected_ips == expected_ips