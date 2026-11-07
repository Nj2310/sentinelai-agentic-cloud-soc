# SentinelAI — AI-Powered SOC Investigation Lab

## Project Overview

SentinelAI is an independent cybersecurity research and development project focused on building an AI-assisted Security Operations Center (SOC) investigation workflow.

The project combines security event analysis, detection engineering, incident response, threat intelligence, and AI-assisted automation.

Development begins with Python-based rule-driven detection and will progressively explore AI-assisted security investigation capabilities.

## Project Objectives

1. Build a Python-based security log ingestion pipeline.
2. Detect suspicious activity using rule-based detection techniques.
3. Classify and prioritize security alerts.
4. Map detected activity to MITRE ATT&CK techniques.
5. Document investigations using the NIST SP 800-61 framework.
6. Develop an AI-assisted alert enrichment and investigation workflow.
7. Evaluate detection performance using precision, recall, and F1-score.
8. Research prompt injection risks in AI-assisted security workflows.

## Technology Stack

**Currently Used**
- Python
- CSV and JSON
- Python standard library
- Git and GitHub
- Visual Studio Code

**Planned Technologies**
- Pandas
- Pytest
- Scikit-learn
- MITRE ATT&CK
- NIST SP 800-61
- LLM APIs
- Model Context Protocol (MCP)

## Development Status

**Status:** In Development

**Current Phase:** Day 2 — Detection Engineering and Performance Evaluation

### Day 1 — Environment Setup and Initial Detection

- Established the Python development environment.
- Created the initial project structure.
- Implemented authentication log ingestion.
- Developed a rule-based brute-force detection engine.
- Added structured JSON security alert generation.
- Mapped brute-force activity to MITRE ATT&CK T1110.
- Initialized Git version control and GitHub repository.

### Day 2 — Detection Evaluation and Testing

- Implemented ground-truth validation using labeled authentication logs.
- Developed a confusion matrix evaluator.
- Calculated accuracy, precision, recall, and F1 score.
- Added false positive rate calculation.
- Updated the detector to accept configurable input datasets.
- Tested benign authentication activity below the detection threshold.
- Tested simulated malicious brute-force activity.
- Verified structured JSON alert generation.

## Detection Methodology

The initial detection engine identifies potential brute-force attacks based on repeated failed authentication attempts from the same source IP address.

**Current Detection Rule:**
- Threshold: 5 failed authentication attempts
- Time Window: 5 minutes
- Detection Unit: Source IP address
- Severity: HIGH
- MITRE ATT&CK Technique: T1110 — Brute Force

The detector supports multiple authentication failure status representations and can process different CSV datasets.

## Preliminary Detection Evaluation

The initial evaluation used a small synthetic dataset containing six unique source IP addresses: five labeled benign and one labeled malicious.

### Confusion Matrix

| Metric | Result |
|---|---|
| True Positives (TP) | 1 |
| False Positives (FP) | 0 |
| True Negatives (TN) | 5 |
| False Negatives (FN) | 0 |

### Performance Metrics

| Metric | Result |
|---|---|
| Accuracy | 100.00% |
| Precision | 100.00% |
| Recall | 100.00% |
| F1 Score | 100.00% |
| False Positive Rate | 0.00% |

**Evaluation Limitation:** These results reflect performance on a very small, synthetic dataset. They should not be interpreted as validated real-world detection effectiveness. Future evaluations will incorporate larger datasets, more varied attack patterns, and challenging benign scenarios.

## Controlled Test Scenarios

| Scenario | Expected Behavior | Observed Behavior | Result |
|---|---|---|---|
| Three failed logins followed by a successful login | No alert | No alert | Passed |
| Five failed logins within two minutes | Brute-force alert | Alert generated | Passed |

The malicious test also confirmed successful JSON alert generation containing severity, source IP, failed attempt count, detection timestamp, MITRE ATT&CK mapping, and recommended investigation action.

## Project Scope

SentinelAI is an independent, hands-on cybersecurity research prototype.

Initial development uses synthetic security logs and simulated security incidents.

Production SIEM, EDR, and cloud security integrations are potential future enhancements and will be documented separately if implemented.

## Future Development

- Expand authentication test coverage and evaluate additional detection edge cases.
- Develop automated tests for detection rules.
- Improve detection reporting and visualization.
- Explore alert enrichment and threat intelligence integration.
- Investigate AI-assisted SOC workflows.
- Research prompt injection risks and security controls for AI-assisted investigations.

## Disclaimer

SentinelAI is an educational and research project. All simulated incidents and preliminary evaluation results are clearly labeled.

The current implementation is a research prototype and is not intended for production security monitoring.


## Automated Detection Testing

SentinelAI uses Pytest to validate its rule-based brute-force
detection engine.

### Test Scenarios

The automated test suite covers five scenarios:

1. **Benign Authentication:** Three failed login attempts
   do not trigger an alert.
2. **Brute-Force Detection:** Five rapid failed login
   attempts trigger an alert.
3. **Threshold Boundary:** Four failed login attempts
   remain below the detection threshold.
4. **Time-Window Validation:** Five failed attempts spread
   across 20 minutes do not trigger an alert.
5. **Exact Time Boundary:** Five failed attempts spanning
   exactly five minutes trigger an alert.

### Running the Tests

Install Pytest in your Python environment:

```bash
python -m pip install pytest
```

Run the automated test suite:

```bash
python -m pytest tests/test_detector.py -v
```

### Test Fixtures

Synthetic authentication datasets are stored in
`tests/fixtures/`.

These datasets are version-controlled to support
reproducible testing without exposing real authentication logs.

### Preliminary Results

All five automated tests passed during local validation
using Python 3.13.17 and Pytest 9.2.0.

These results validate the tested rule behavior on synthetic
datasets and do not establish real-world detection accuracy.
