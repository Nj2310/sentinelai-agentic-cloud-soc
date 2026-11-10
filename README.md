# SentinelAI — Agentic AI Cloud Security Operations Platform

**A Local-First Cybersecurity Research and Development Project**

Python | AWS CloudTrail | Detection Engineering | SOC Investigation | Agentic AI (Planned) | Cloud Security

## Project Overview

SentinelAI is an independent cybersecurity research and development project focused on building an AI-assisted, agentic Security Operations Center (SOC) investigation platform for cloud security monitoring and incident analysis.

The project integrates security log ingestion, detection engineering, AWS CloudTrail analysis, Identity and Access Management (IAM) monitoring, automated evidence collection, and structured security investigation workflows.

SentinelAI is being developed incrementally, beginning with deterministic Python-based security detections and progressing toward intelligent, tool-using AI agents capable of assisting security analysts with investigation, contextual analysis, risk assessment, and incident reporting.

The long-term objective is to explore how agentic AI can improve cloud security operations while maintaining transparency, explainability, human oversight, and secure automation practices.

**Current implementation:** A functional, locally executed security detection and investigation prototype using synthetic authentication and AWS CloudTrail datasets.

**Future direction:** Integration of local large language models (LLMs), agent orchestration, machine learning, and interactive security dashboards.

---

## Project Objectives

1. Build a Python-based security log ingestion and normalization pipeline.
2. Analyze authentication activity and AWS CloudTrail security events.
3. Develop rule-based detection mechanisms for suspicious security activity.
4. Identify security-relevant IAM operations and credential creation events.
5. Classify, prioritize, and enrich security alerts.
6. Map applicable security detections to MITRE ATT&CK techniques.
7. Develop automated SOC investigation and evidence-gathering workflows.
8. Integrate local LLMs for AI-assisted security investigation and incident summarization.
9. Explore agentic AI frameworks for controlled tool use and multi-step investigations.
10. Evaluate detection effectiveness using accuracy, precision, recall, F1-score, and false positive rate.
11. Apply incident response principles informed by NIST SP 800-61.
12. Research prompt injection, tool misuse, and other security risks associated with AI-assisted SOC operations.
13. Develop a modular, testable, and reproducible cloud security research platform.

---

## Technology Stack

### Currently Implemented

| Technology | Purpose |
|---|---|
| Python 3.13 | Core application development |
| Python Standard Library | Log processing, timestamps, data structures, and JSON handling |
| CSV and JSON | Security event ingestion and structured data |
| AWS CloudTrail-Style Logs | Synthetic cloud authentication and IAM event analysis |
| Pytest | Automated security detection and investigation testing |
| unittest.mock | Isolated investigation workflow testing |
| Git and GitHub | Version control and project documentation |
| Visual Studio Code | Development environment |

### Planned Technologies

| Technology | Planned Purpose |
|---|---|
| Ollama | Local LLM inference |
| Local LLM | AI-assisted investigation and incident summaries |
| LangGraph | Stateful agent orchestration and controlled tool execution |
| Scikit-learn | Machine learning and anomaly detection |
| Pandas | Data processing and exploratory analysis |
| Streamlit | Interactive SOC monitoring dashboard |
| MITRE ATT&CK | Expanded detection mapping and investigation context |
| NIST SP 800-61 | Incident response methodology |
| Terraform | Infrastructure-as-code research and configuration |
| GitHub Actions | Automated testing and CI workflows |
| Model Context Protocol (MCP) | Research into standardized AI tool integrations |

Planned technologies are not yet integrated unless explicitly documented in a future development update.

---

## System Architecture

The current architecture separates security event ingestion, detection logic, and investigation workflows.

```text
              Synthetic Security Data
                       |
          +------------+------------+
          |                         |
    Authentication Logs       AWS CloudTrail
          |                         |
          |                +--------+--------+
          |                |                 |
          |           ConsoleLogin     IAM API Events
          |                |                 |
          +----------------+-----------------+
                           |
                  Security Parsers
                           |
                  Detection Engines
                           |
                Structured Security Alerts
                           |
                    SOC Investigator
                           |
                  Evidence Lookup Tool
                           |
                Investigation Findings
                           |
                Recommended Actions
```

### Planned Agentic AI Architecture

```text
               Security Alerts
                      |
                      v
             Agentic SOC Investigator
                      |
             Investigation State
                      |
             +--------+--------+
             |                 |
       Evidence Tools     Local LLM
             |                 |
       Log Correlation    Context Analysis
             |                 |
             +--------+--------+
                      |
                Risk Assessment
                      |
              Incident Summary
                      |
             Human Analyst Review
                      |
                 SOC Dashboard
```

The planned agentic architecture will prioritize read-only investigation tools, controlled execution, evidence-based conclusions, and human approval for potentially disruptive security actions.

---

## Implemented Security Capabilities

### 1. Authentication Brute-Force Detection

SentinelAI detects potential brute-force authentication attempts by analyzing repeated failed login events originating from the same source IP address.

**Detection Configuration**

| Parameter | Value |
|---|---|
| Detection Type | Brute-Force Authentication |
| Failure Threshold | 5 failed login attempts |
| Time Window | 5 minutes |
| Detection Unit | Source IP Address |
| Alert Severity | HIGH |
| MITRE ATT&CK | T1110 — Brute Force |

The detection engine supports:

- CSV authentication log ingestion.
- Configurable input datasets.
- Authentication failure status normalization.
- Timestamp parsing and chronological event ordering.
- Sliding-window detection logic.
- Duplicate alert prevention for the same source IP within a detection run.
- Structured JSON alert generation.
- Optional alert persistence for isolated testing.
- Graceful handling of invalid timestamps and missing source IP addresses.

### 2. AWS CloudTrail Authentication Analysis

SentinelAI supports local analysis of synthetic AWS CloudTrail JSON events.

The CloudTrail parser identifies AWS ConsoleLogin activity and normalizes relevant event fields for processing by the existing brute-force detection engine.

Normalized fields include:

- Timestamp
- Source IP address
- Username
- Authentication status

The existing brute-force detection logic can process normalized CloudTrail events without requiring a separate authentication detection algorithm.

**Current Dataset**

The synthetic CloudTrail authentication dataset contains six ConsoleLogin events, including five failed login attempts associated with one source IP address.

The integrated detection engine successfully identifies the simulated brute-force activity.

No live AWS account, deployed AWS infrastructure, or production CloudTrail integration is required for the current implementation.

### 3. AWS IAM Security Detection

SentinelAI includes a dedicated IAM event parser and security detection engine.

The parser extracts `CreateAccessKey` operations from synthetic AWS CloudTrail-style events.

Relevant fields include:

- Event timestamp
- AWS API operation
- Source IP address
- IAM actor
- Target IAM user

**Implemented Detection Rule: IAM Self-Service Access Key Creation**

The detection engine flags events where an IAM user creates an access key for their own account.

| Parameter | Value |
|---|---|
| Detection Type | IAM Self-Service Access Key Creation |
| AWS API Operation | CreateAccessKey |
| Detection Condition | Actor equals target IAM user |
| Alert Severity | MEDIUM |
| Alert Status | needs_investigation |

This activity is not inherently malicious. The rule identifies an event requiring contextual investigation rather than confirming account compromise.

The synthetic IAM dataset includes two access key creation events: one administrative example and one simulated suspicious self-service event.

The detector generates one investigation alert for the self-service event.

### 4. Automated SOC Investigation Workflow

SentinelAI includes an initial deterministic SOC Investigator implemented in Python.

The investigator accepts IAM security alerts and generates structured investigation reports.

Current report fields include:

- Alert type
- IAM actor
- Source IP address
- Severity
- Investigation findings
- Recommended actions
- Investigation status
- Associated login evidence

The investigator currently uses predefined rules and recommendations. It does not yet perform LLM-based reasoning or autonomous investigation planning.

### 5. Read-Only Investigation Tools

SentinelAI includes a CloudTrail login activity lookup tool.

The tool retrieves normalized authentication events associated with a specified source IP address.

Current capabilities include:

- Searching locally available synthetic CloudTrail events.
- Filtering authentication records by source IP.
- Returning matching events.
- Reporting the number of matching events.
- Integrating evidence results into structured investigation reports.

When no matching events exist in the available dataset, the investigator explicitly reports that no matching login activity was found.

**Important:** Absence of matching events in a limited dataset does not establish that an account or IP address is safe.

These investigation tools form the foundation for future agent-directed evidence gathering.

---

## Preliminary Detection Evaluation

The initial brute-force detection evaluation used a small synthetic dataset containing six unique source IP addresses: five labeled benign and one labeled malicious.

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

**Evaluation Limitation:** These results reflect performance on a very small, synthetic dataset and should not be interpreted as validated real-world detection effectiveness.

Future evaluation will include larger datasets, additional benign scenarios, more varied attack patterns, and adversarial testing.

---

## Automated Testing

SentinelAI uses Pytest to validate security detection and investigation behavior.

**Latest verified result: 13 automated tests passed.**

### Test Coverage

| Component | Test Coverage | Tests |
|---|---|---|
| Authentication Detection | Thresholds, time windows, alert persistence, malformed records, CloudTrail integration | 10 |
| IAM Detection | Self-service access key creation and administrative activity | 2 |
| SOC Investigation | Missing login evidence and mocked tool invocation | 1 |
| **Total** | | **13** |

The automated tests validate:

- Benign authentication behavior.
- Brute-force detection thresholds.
- Detection time-window boundaries.
- Alert generation and optional persistence.
- Invalid timestamp handling.
- Missing source IP handling.
- AWS CloudTrail authentication integration.
- IAM self-service access key creation.
- Administrative access key creation exclusions.
- SOC investigation evidence lookup behavior.

### Running the Tests

Install Pytest in your Python environment:

```bash
python -m pip install pytest
```

Run the complete automated test suite:

```bash
python -m pytest -v
```

Run an individual component:

```bash
python -m pytest tests/test_detector.py -v
python -m pytest tests/test_iam_detector.py -v
python -m pytest tests/test_investigator.py -v
```

### Latest Test Environment

- Python: 3.13.17
- Pytest: 9.2.0
- Operating System: Windows
- Result: 13 passed

These tests validate specific behaviors against synthetic inputs. They do not establish production readiness or real-world detection accuracy.

---

## Running SentinelAI Locally

### Prerequisites

- Python 3.13 or a compatible Python version.
- Git.
- Visual Studio Code or another Python-compatible editor.
- Pytest for automated testing.

### Clone the Repository

```bash
git clone https://github.com/Nj2310/sentinelai-soc-lab.git
cd sentinelai-soc-lab
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Test Dependencies

```bash
python -m pip install pytest
```

### Run the Authentication Detection Engine

```bash
python src/detector.py
```

### Run the CloudTrail Authentication Parser and Detection

```bash
python src/cloudtrail_parser.py
```

### Run the IAM Event Parser

```bash
python src/iam_parser.py
```

### Run the IAM Detection Engine

```bash
python src/iam_detector.py
```

### Run the SOC Investigator

```bash
python src/agents/investigator.py
```

### Run the CloudTrail Evidence Lookup Tool

```bash
python src/agents/investigation_tools.py
```

### Run All Automated Tests

```bash
python -m pytest -v
```

The current prototype operates locally using synthetic security datasets. AWS credentials and paid cloud services are not required.

---

## Development Progress

**Project Status:** Active Development

**Current Phase:** Day 6 — IAM Security Detection and SOC Investigation Foundation

### Day 1 — Environment Setup and Initial Detection

- Established the Python development environment.
- Created the initial project structure.
- Implemented authentication log ingestion.
- Developed a rule-based brute-force detection engine.
- Added structured JSON security alert generation.
- Mapped brute-force activity to MITRE ATT&CK T1110.
- Initialized Git version control and GitHub repository.

**Status: Completed**

### Day 2 — Detection Evaluation and Testing

- Implemented ground-truth validation using labeled authentication logs.
- Developed a confusion matrix evaluator.
- Calculated accuracy, precision, recall, F1-score, and false positive rate.
- Evaluated benign and simulated malicious authentication activity.
- Documented limitations of the synthetic evaluation dataset.

**Status: Completed**

### Day 3 — Automated Detection Testing

- Integrated Pytest.
- Developed five initial automated detection tests.
- Tested authentication thresholds and time-window boundaries.
- Created reusable synthetic test fixtures.

**Status: Completed**

### Day 4 — Detection Reliability Improvements

- Added optional alert persistence controls.
- Improved handling of invalid timestamps.
- Added validation for missing source IP addresses.
- Expanded automated testing.
- Improved test isolation using mocked dependencies.

**Status: Completed**

### Day 5 — AWS CloudTrail Integration

- Created a synthetic AWS CloudTrail authentication dataset.
- Implemented CloudTrail JSON parsing.
- Normalized AWS ConsoleLogin records.
- Integrated CloudTrail authentication events with the existing detection engine.
- Added automated integration testing.

**Status: Completed**

### Day 6 — IAM Security Detection and SOC Investigation Foundation

- Created synthetic AWS IAM CloudTrail events.
- Implemented IAM CreateAccessKey event parsing.
- Developed self-service access key creation detection.
- Added IAM detection tests.
- Created a structured SOC investigation workflow.
- Developed a read-only CloudTrail evidence lookup tool.
- Integrated evidence retrieval into investigation reports.
- Added automated investigator testing.
- Verified all 13 automated tests.

**Status: Implementation completed; repository publication in progress**

---

## Agentic AI Development Roadmap

The next development phase will focus on introducing actual AI capabilities.

### Phase 1 — Local LLM Integration

- Evaluate hardware requirements for local inference.
- Install and configure Ollama.
- Select a suitable local language model.
- Develop structured prompts for security investigation.
- Generate AI-assisted explanations from security evidence.

### Phase 2 — Agentic Investigation Workflows

- Explore LangGraph for investigation orchestration.
- Implement explicit investigation states and transitions.
- Allow controlled selection of read-only investigation tools.
- Correlate authentication and IAM security events.
- Introduce investigation stopping conditions and execution limits.
- Preserve evidence provenance and auditability.

### Phase 3 — Intelligent Security Analysis

- Explore machine learning-based anomaly detection.
- Implement contextual risk scoring.
- Develop alert prioritization workflows.
- Evaluate AI-generated findings against known synthetic scenarios.
- Measure unsupported claims and investigation errors.

### Phase 4 — Security Controls for AI Agents

- Investigate prompt injection vulnerabilities.
- Validate tool inputs and outputs.
- Restrict agent permissions.
- Introduce human approval for potentially disruptive actions.
- Explore least-privilege execution and tool allowlisting.
- Test agent behavior against adversarial security data.

### Phase 5 — SOC Dashboard and Automation

- Develop a Streamlit-based dashboard.
- Visualize authentication and IAM security alerts.
- Display investigation evidence and AI-generated findings.
- Generate structured incident reports.
- Introduce GitHub Actions for continuous testing.
- Explore infrastructure-as-code security research using Terraform.

---

## Security and Responsible AI Principles

SentinelAI follows a local-first, security-conscious development approach.

Key principles include:

1. **Synthetic Data:** Use simulated security events rather than sensitive production logs.
2. **Read-Only Investigation:** Prioritize evidence gathering over automated infrastructure changes.
3. **Human Oversight:** Require human approval before potentially disruptive response actions.
4. **Explainability:** Associate investigation findings with supporting evidence.
5. **Least Privilege:** Restrict future agent tools to necessary permissions.
6. **Reproducibility:** Maintain automated tests and version-controlled datasets.
7. **Transparent Evaluation:** Clearly distinguish synthetic test results from production performance.
8. **Responsible AI:** Research hallucinations, prompt injection, and unsafe tool execution before enabling more autonomous behavior.

These principles guide the planned architecture; not all controls have been implemented yet.

---

## Project Scope and Limitations

SentinelAI is an independent, hands-on cybersecurity research prototype.

Current development uses synthetic authentication records and AWS CloudTrail-style JSON events.

The platform does not currently:

- Connect to live AWS accounts.
- Collect production CloudTrail telemetry.
- Use a deployed SIEM or EDR platform.
- Run an integrated large language model.
- Perform autonomous AI investigation planning.
- Execute automated cloud remediation.
- Provide production-grade incident response capabilities.

These features may be explored in later phases and will be documented separately if implemented.

---

## Future Research Directions

- Advanced AWS IAM threat detection.
- CloudTrail event correlation and behavioral analysis.
- AI-assisted incident triage and investigation.
- Agentic AI orchestration and secure tool execution.
- Cloud identity anomaly detection.
- Threat intelligence enrichment.
- Prompt injection defense in security workflows.
- LLM output validation and evidence grounding.
- Incident response reporting aligned with NIST guidance.
- Automated security evaluation and CI pipelines.

---

## Disclaimer

SentinelAI is an educational and research project intended for hands-on learning, experimentation, and cybersecurity portfolio development.

All simulated incidents and preliminary evaluation results are clearly identified.

The current implementation is not intended for production security monitoring or autonomous incident response.

Security detections, AI-generated recommendations, and future automation capabilities must be independently validated before use in operational environments.

## Day 7 — Local LLM Integration (Qwen3 + Ollama)

Integrated a locally hosted Qwen3 4B language model into SentinelAI's SOC investigation workflow using Ollama.

### Implemented Features

- Installed Ollama and downloaded the Qwen3 4B model for local inference.
- Created `src/agents/llm_client.py` to generate AI-assisted security investigation summaries.
- Connected the LLM client to the existing SOC Investigator through an optional `use_ai` parameter.
- Preserved deterministic IAM detection and read-only CloudTrail evidence collection.
- Added evidence-grounding instructions to reduce unsupported security conclusions.
- Generated investigation summaries containing observed activity, risk assessments, and recommended analyst investigation steps.
- Added mocked unit tests for the LLM client and AI-enabled investigator.

### Validation

- **15 automated tests passed** using pytest.
- Successfully ran an end-to-end AI-assisted investigation against synthetic AWS IAM and CloudTrail events.
- Verified that the updated AI prompt avoided claiming confirmed account compromise without supporting evidence.

### Technology Stack

Python, pytest, AWS CloudTrail (synthetic data), Ollama, Qwen3 4B.

### Security and Cost Considerations

- All model inference runs locally through Ollama.
- No paid LLM API or AWS deployment is required.
- Investigation tools are read-only.
- AI-generated findings are advisory and require analyst verification.
- Prompt instructions reduce hallucination risk but do not guarantee factual accuracy.