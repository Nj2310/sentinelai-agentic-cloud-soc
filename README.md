SentinelAI — Agentic AI Cloud Security Operations Platform
A Local-First Cybersecurity Research and Development Project

Python | AWS CloudTrail | Detection Engineering | SOC Investigation | Local Qwen3 AI | Controlled Tool Use | Cloud Security
Project Overview
SentinelAI is an independent cybersecurity research and development project focused on an AI-assisted Security Operations Center (SOC) investigation platform for cloud security monitoring and incident analysis.

The project combines security log ingestion, detection engineering, synthetic AWS CloudTrail analysis, Identity and Access Management (IAM) monitoring, evidence collection, and structured investigation workflows. Development is incremental: deterministic Python detections provide the foundation, while a locally hosted language model can propose approved investigation tools and produce advisory security analysis.

Current implementation: A working local prototype with rule-based detections, IAM investigation, Ollama-hosted Qwen3 4B analysis, and a single-step AI-selected, read-only CloudTrail lookup workflow.

Future direction: Multi-step agent orchestration, broader event correlation, machine learning, dashboard visualization, and stronger security evaluation.

No live AWS account, paid LLM API, or deployed cloud infrastructure is required.
Project Objectives
1. Build a Python-based security log ingestion and normalization pipeline.
2. Analyze authentication activity and AWS CloudTrail security events.
3. Develop rule-based detections for suspicious security activity.
4. Identify security-relevant IAM operations and credential creation events.
5. Classify, prioritize, and enrich security alerts.
6. Map applicable detections to MITRE ATT&CK techniques.
7. Develop SOC investigation and evidence-gathering workflows.
8. Integrate local LLMs for AI-assisted investigation and incident summaries.
9. Explore controlled agentic tool use and multi-step investigation orchestration.
10. Evaluate detection effectiveness using accuracy, precision, recall, F1-score, and false positive rate.
11. Apply incident response principles informed by NIST SP 800-61.
12. Research prompt injection, tool misuse, and security risks in AI-assisted SOC operations.
13. Maintain a modular, testable, reproducible cloud security research platform.
Technology Stack
Currently Implemented
Technology	Purpose
Python 3.13	Core application and security detection logic
Python standard library	CSV/JSON processing, timestamps, ipaddress, data validation
Synthetic AWS CloudTrail-style JSON	Authentication and IAM event analysis
Pytest	Automated detection, investigator, and workflow tests
unittest.mock	Isolated LLM and tool execution testing
Ollama	Local model inference
Qwen3 4B (qwen3:4b)	AI-assisted investigation summaries and tool selection
Git and GitHub	Version control and documentation
Visual Studio Code	Local development environment


Planned / Research Technologies
Technology	Planned Purpose
LangGraph	Stateful, multi-step agent orchestration
Scikit-learn	Anomaly detection and machine learning
Pandas	Data exploration and transformation
Streamlit	Interactive SOC monitoring dashboard
Terraform	Infrastructure-as-code research
GitHub Actions	Automated CI testing
Model Context Protocol (MCP)	Research into standardized tool integrations
MITRE ATT&CK	Expanded technique mapping and investigation context
NIST SP 800-61	Incident response methodology


Planned technologies are not yet integrated unless documented in a subsequent update.
System Architecture
Current Implementation
                  Synthetic Security Data
                           |
              +------------+------------+
              |                         |
       Authentication CSV        AWS CloudTrail JSON
                                        |
                               +--------+--------+
                               |                 |
                          ConsoleLogin     IAM CreateAccessKey
                               |                 |
              +----------------+-----------------+
                               |
                        Event Parsers
                               |
                       Detection Engines
                               |
                     Structured Security Alerts
                               |
              +----------------+----------------+
              |                                 |
       Deterministic SOC                 Agentic Workflow
         Investigator                          |
              |                        Local Qwen3 4B
       Read-only Evidence                  Tool Selector
              |                                 |
       Optional Qwen3 Summary          Tool/Parameter Checks
              |                                 |
       Investigation Findings         Allowlisted Tool Executor
                                                |
                                        Read-only Login Lookup
                                                |
                                         Investigation Result
The current agentic workflow performs one model-selected tool call at most. It does not implement iterative planning, LangGraph state management, or autonomous remediation.
Planned Extended Architecture
Security Alerts -> Stateful Agent Orchestration
                       |
               Investigation State
                       |
              Read-only Evidence Tools
                       |
               Event Correlation
                       |
              Context / Risk Analysis
                       |
              Evidence-based Summary
                       |
                Human Analyst Review
                       |
                  SOC Dashboard
Implemented Security Capabilities
1. Authentication Brute-Force Detection
SentinelAI identifies potential brute-force authentication attempts from repeated failed logins originating from the same source IP.
Parameter	Value
Detection type	Brute-force authentication
Failure threshold	5 failed login attempts
Time window	5 minutes
Detection unit	Source IP address
Alert severity	HIGH
MITRE ATT&CK	T1110 — Brute Force


Features include CSV ingestion, normalized authentication statuses, timestamp parsing and chronological ordering, sliding-window detection, duplicate-alert prevention within a run, structured JSON alerts, optional alert persistence, and graceful skipping of malformed timestamps or missing source IPs.
2. AWS CloudTrail Authentication Analysis
The local CloudTrail parser extracts and normalizes synthetic ConsoleLogin events into timestamp, source IP, username, and authentication status. The existing brute-force detection logic processes these normalized records.

The example dataset contains six console login events, including five failed logins from 198.51.100.50 and one successful login from another IP. The detector identifies the simulated brute-force activity. This is synthetic data, not a live AWS integration.
3. AWS IAM Security Detection
The IAM parser processes synthetic CreateAccessKey events, including event time, API operation, source IP, actor, and target user.

Implemented rule: IAM self-service access key creation
Parameter	Value
AWS API operation	CreateAccessKey
Detection condition	Actor equals target IAM user
Alert severity	MEDIUM
Alert status	needs_investigation


The synthetic IAM dataset contains two access key creation events: an administrative example and a self-service example. The latter produces an investigation alert. Self-service key creation is not inherently malicious and does not prove account compromise.
4. Deterministic SOC Investigator
src/agents/investigator.py accepts IAM alerts and produces structured investigation results, including alert details, login evidence, findings, recommended analyst actions, and investigation status.

The investigator uses a read-only login lookup and supports optional AI analysis via investigate_alert(alert, use_ai=True). Without that option, investigation remains deterministic.
5. Read-Only CloudTrail Evidence Lookup
src/agents/investigation_tools.py provides lookup_login_activity(source_ip), which searches locally available synthetic ConsoleLogin records and returns matching events and an event count.

When no matching events are found, that result applies only to the available dataset; it does not establish that an account or IP is safe.
6. Local LLM-Assisted Investigation (Day 7)
src/agents/llm_client.py uses Ollama and qwen3:4b to produce advisory security analysis based on supplied investigation evidence. The prompt asks the model to distinguish observations from suspicions, avoid inventing evidence, and recommend human review rather than automatic blocking.

Prompt instructions can reduce unsupported conclusions but cannot guarantee factual accuracy or prompt-injection resistance. AI output is advisory and must be checked against evidence.
7. Controlled AI Tool Selection and Execution (Day 8)
The agentic workflow introduces four modules:
File	Responsibility
src/agents/tool_registry.py	Lists approved tools and exposes their metadata
src/agents/tool_selector.py	Requests a JSON tool recommendation from local Qwen3 and validates it
src/agents/tool_executor.py	Rejects unregistered tools and invalid parameter sets before execution
src/agents/agentic_workflow.py	Connects tool selection to a single read-only investigation call


Current approved tool: lookup_login_activity, requiring source_ip.

The selector uses Ollama's JSON schema output mode, checks tool names and parameter structure, and derives the final lookup IP from the original alert rather than the LLM's copied value. It also checks the original IP with Python's ipaddress module.

The executor rejects unauthorized tool names, missing parameters, and unexpected parameters. A tool's read_only registry flag is a policy declaration; it is not an independent sandbox or runtime permission boundary. Only reviewed read-only functions should be registered.

Verified end-to-end scenario: For a synthetic brute-force alert, Qwen3 selected lookup_login_activity. Although the model incorrectly reproduced the IP as 198.5:100.50, application logic supplied the validated original 198.51.100.50 to the executor. The lookup returned five matching failed login events, and the workflow completed successfully.

This is single-step, AI-directed tool selection, not autonomous multi-step investigation or AWS remediation.
Preliminary Detection Evaluation
The initial brute-force evaluation used a small synthetic dataset containing six unique source IP addresses: five labeled benign and one labeled malicious.
Confusion Matrix
Metric	Result
True positives (TP)	1
False positives (FP)	0
True negatives (TN)	5
False negatives (FN)	0


Performance Metrics
Metric	Result
Accuracy	100.00%
Precision	100.00%
Recall	100.00%
F1 score	100.00%
False positive rate	0.00%


Evaluation limitation: These figures describe a very small synthetic test set and are not evidence of real-world detection effectiveness. Future evaluation should include larger datasets, more benign scenarios, varied attack patterns, and adversarial tests.
Automated Testing
Latest verified result: 25 tests passed in 1.50 seconds on Windows using Python 3.13.17 and pytest 9.2.0.
Component	Covered behaviors	Tests
Authentication detection	Thresholds, windows, malformed input, alert persistence, CloudTrail integration	10
IAM detection	Self-service and administrative access key events	2
SOC investigator	Missing login evidence; mocked AI-enabled investigation	2
LLM client	Mocked Ollama analysis	1
Tool executor	Approved execution, unauthorized tools, missing/extra parameters	4
AI tool selector	Original IP preservation, invalid IP, unauthorized tools, unexpected fields	4
Agentic workflow	Selected-tool execution and no-tool path (mocked)	2
Total		25


The tests use synthetic inputs and mocks. The end-to-end Day 8 scenario was also run manually against the local model and CloudTrail fixture. Neither the tests nor the manual scenario establish production readiness.

Run the entire suite:
python -m pytest -v
Run component tests:
python -m pytest tests/test_detector.py -v
python -m pytest tests/test_iam_detector.py -v
python -m pytest tests/test_investigator.py -v
python -m pytest tests/test_llm_client.py -v
python -m pytest tests/test_tool_executor.py -v
python -m pytest tests/test_tool_selector.py -v
python -m pytest tests/test_agentic_workflow.py -v
Running SentinelAI Locally
Prerequisites
- Python 3.13 (tested version: 3.13.17)
- Git and a Python-compatible editor such as Visual Studio Code
- Ollama and the local Qwen3 4B model for AI-enabled workflows
- Pytest for automated tests
Clone the Repository
git clone https://github.com/Nj2310/sentinelai-agentic-cloud-soc.git
cd sentinelai-agentic-cloud-soc
Create and Activate a Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install Python Dependencies
python -m pip install pytest ollama
Prepare the Local Model (for AI Features)
Install Ollama separately, then download the model:
ollama pull qwen3:4b
Ensure the Ollama service is running before using AI-enabled workflows. Non-AI detection tests can run without model inference.
Run Parsers and Detectors
python src/detector.py
python src/cloudtrail_parser.py
python src/iam_parser.py
python src/iam_detector.py
Run a Single-Step Agentic Investigation
From the repository root, with Ollama available:
python -c "from src.agents.agentic_workflow import run_agentic_investigation; import json; alert = {'alert_type': 'BRUTE_FORCE', 'source_ip': '198.51.100.50', 'severity': 'high', 'description': 'Five failed login attempts from the same IP address'}; print(json.dumps(run_agentic_investigation(alert), indent=2))"
This example uses synthetic local CloudTrail data. It asks Qwen3 to select an approved tool and then performs a validated, read-only lookup. Local model inference may take time on CPU-based hardware.
Run All Tests
python -m pytest -v
Development Progress
Project status: Active development
Current phase: Day 8 — Controlled Agentic Investigation Workflow (implemented and locally verified; documentation/commit pending)
Day 1 — Environment Setup and Initial Detection
- Set up Python, project structure, Git, and GitHub.
- Implemented CSV authentication ingestion and brute-force detection.
- Added JSON alerts and MITRE ATT&CK T1110 mapping.
Status: Completed
Day 2 — Detection Evaluation
- Implemented labeled synthetic evaluation and confusion matrix metrics.
- Documented the limits of the small evaluation dataset.
Status: Completed
Day 3 — Automated Detection Testing
- Integrated pytest, five initial tests, and reusable fixtures.
Status: Completed
Day 4 — Detection Reliability Improvements
- Added optional alert persistence and handling for invalid timestamps/missing IPs.
- Expanded tests and improved isolation.
Status: Completed
Day 5 — AWS CloudTrail Integration
- Created synthetic ConsoleLogin events and a normalization parser.
- Connected CloudTrail authentication events to the existing detector.
Status: Completed
Day 6 — IAM Detection and Investigation Foundation
- Created synthetic IAM CreateAccessKey events.
- Implemented IAM parsing and self-service access key detection.
- Added deterministic investigation and read-only login evidence lookup.
- Verified 13 automated tests.
Status: Completed
Day 7 — Local LLM Integration (Qwen3 + Ollama)
- Installed Ollama and downloaded qwen3:4b for local inference.
- Created src/agents/llm_client.py and optional AI-enabled investigator analysis.
- Added evidence-grounding prompt instructions and mocked tests.
- Ran an AI-assisted IAM investigation on synthetic evidence.
- Verified 15 automated tests and pushed Day 7 changes to GitHub.
Status: Completed and published
Day 8 — Controlled Agentic Tool Selection and Execution
- Implemented an allowlisted tool registry and read-only tool executor.
- Added validation for unauthorized tools and missing/unexpected parameters.
- Integrated Qwen3-based JSON tool selection using an explicit response schema.
- Prevented model-generated IP transcription errors from changing the lookup target.
- Added original alert IP format validation using ipaddress.
- Connected AI tool selection with the controlled executor in a single-step workflow.
- Verified an end-to-end synthetic brute-force investigation returning five matching login events.
- Added automated selector, executor, and workflow tests.
- Verified the complete suite: 25 tests passed.
Status: Implementation and local validation completed; README update and Git commit pending
Agentic AI Development Roadmap
Phase 1 — Local LLM Integration
Implemented: Local Ollama/Qwen3 inference, AI-assisted investigation summaries, and structured prompting.

Further work: Evaluation of factuality, latency, and adversarial prompt behavior.
Phase 2 — Agentic Investigation Workflows
Implemented: One-step AI tool recommendation, approved-tool registry, parameter validation, and controlled read-only execution.

Planned: LangGraph orchestration, explicit investigation state, multi-step correlation, execution limits, stopping conditions, and richer audit trails.
Phase 3 — Intelligent Security Analysis
- Explore machine learning-based anomaly detection.
- Implement contextual risk scoring and alert prioritization.
- Evaluate AI-generated findings against known synthetic scenarios.
- Measure unsupported claims and investigation errors.
Phase 4 — Security Controls for AI Agents
Implemented in prototype: Tool allowlisting, basic schema/parameter checks, original alert IP validation, and read-only tool design.

Planned: Stronger prompt-injection defenses, output validation, independent execution isolation, least-privilege controls, adversarial tests, and human approval mechanisms for any future disruptive actions.
Phase 5 — SOC Dashboard and Automation
- Develop a Streamlit dashboard for alerts, evidence, and AI findings.
- Generate structured incident reports.
- Add GitHub Actions continuous testing.
- Explore Terraform-based cloud security research.
Security and Responsible AI Principles
1. Synthetic data: Avoid exposing sensitive production logs.
2. Read-only investigation: Favor evidence collection over infrastructure changes.
3. Human oversight: Treat AI findings as advisory; require approval before any future disruptive response.
4. Evidence grounding: Keep observations distinct from inferences and recommendations.
5. Tool allowlisting: Permit only explicitly registered investigation functions.
6. Parameter integrity: Validate inputs and derive investigation targets from original evidence, not model transcriptions.
7. Reproducibility: Maintain tests and version-controlled synthetic fixtures.
8. Transparent evaluation: Do not generalize small synthetic results to production accuracy.
9. Responsible AI: Continue research into hallucinations, prompt injection, and unsafe tool execution.
These are guiding principles; not all defense-in-depth controls are implemented.
Project Scope and Limitations
SentinelAI is a local-first educational research prototype. It currently uses synthetic authentication and AWS CloudTrail-style records.

The platform does not currently:
- Connect to live AWS accounts or ingest production CloudTrail telemetry.
- Use a deployed SIEM or EDR system.
- Perform autonomous multi-step investigation planning.
- Enforce tool permissions through a separate OS-level sandbox.
- Execute AWS remediation or other disruptive security actions.
- Provide production-grade incident response capabilities.
The tool registry's read_only flag is an application-level policy indicator. Its safety depends on which functions are registered and how execution is controlled. Local LLM output may be malformed, inaccurate, or affected by adversarial input despite schema validation and prompting.
Future Research Directions
- Advanced AWS IAM detections and event correlation.
- Cloud identity anomaly detection and threat intelligence enrichment.
- Stateful, multi-step agent orchestration and auditability.
- Prompt injection and tool misuse testing.
- LLM output validation and evidence provenance.
- Incident response reporting informed by NIST guidance.
- Security evaluation, CI, and interactive SOC dashboards.
Disclaimer
SentinelAI is an educational and research project for hands-on learning, experimentation, and cybersecurity portfolio development. All incidents and datasets described here are synthetic. Preliminary detection metrics are not production performance claims.

The prototype is not intended for production monitoring or autonomous incident response. AI-generated recommendations and any future automation require independent validation and appropriate human oversight before operational use.