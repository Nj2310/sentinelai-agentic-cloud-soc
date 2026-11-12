# SentinelAI — Agentic AI Cloud Security Operations Platform

## Technical Lab Report: Investigation State Management and Auditability

**Project:** SentinelAI — Agentic AI Cloud Security Operations Platform  
**Development Phase:** Day 9  
**Project Type:** Cybersecurity Research and Development  
**Environment:** Python 3.13.17, Windows, Visual Studio Code  
**Technologies:** Python, AWS CloudTrail (Synthetic), Ollama, Qwen3 4B, Pytest  
**Development Approach:** Local-First, AI-Assisted Security Operations  
**Project Status:** Day 9 implementation and automated validation completed

---

## 1. Executive Summary

SentinelAI is a local-first cybersecurity research project designed to explore how artificial intelligence can support Security Operations Center (SOC) investigations through security event detection, automated evidence collection, and controlled investigation workflows.

The platform combines Python-based detection engineering, synthetic AWS CloudTrail analysis, Identity and Access Management (IAM) monitoring, and a locally hosted Qwen3 4B language model through Ollama.

During the earlier development phases, SentinelAI progressed from basic authentication brute-force detection to IAM security monitoring, deterministic SOC investigation, AI-assisted analysis, and controlled AI-directed tool execution.

**Day 9 focused on implementing investigation state management and auditability.** The objective was to make investigation workflows more traceable by introducing unique investigation identifiers, status tracking, execution records, audit logs, tool-call limits, and structured failure handling.

The implementation was validated using automated tests covering investigation initialization, state transitions, execution recording, stopping conditions, successful investigations, and failure scenarios.

**Final validation result: 34 automated tests passed, with zero failures.**

All development and testing were performed locally using synthetic security data. No live AWS account, paid language model API, or production security infrastructure was required.

---

## 2. Introduction

### 2.1 Background

Modern cloud environments generate large volumes of security events, including authentication attempts, IAM operations, and administrative activities. Security analysts must review these events to identify suspicious behavior, investigate potential incidents, and determine appropriate responses.

Traditional rule-based security detections are useful for identifying predefined attack patterns. However, effective incident investigation also requires contextual analysis, evidence correlation, and transparent decision-making.

Agentic AI offers opportunities to assist analysts by selecting investigation tools, retrieving relevant evidence, and generating contextual explanations.

Such systems also introduce security concerns, including inaccurate AI-generated information, unauthorized tool execution, insufficient auditability, and uncontrolled automated actions.

SentinelAI investigates these opportunities and limitations through a controlled, local-first development environment.

### 2.2 Purpose of the Lab

The purpose of Day 9 was to extend SentinelAI's existing AI-directed investigation workflow with structured state management and audit logging.

Before Day 9, the platform could select and execute an approved read-only investigation tool. However, its workflow did not maintain a comprehensive record of investigation progress or execution history.

The Day 9 implementation addresses these limitations by introducing a dedicated investigation state module and integrating it into the existing agentic workflow.

### 2.3 Lab Objectives

The primary objectives were to:

1. Implement structured investigation state initialization.
2. Generate unique identifiers for individual investigations.
3. Track investigation progress through defined statuses.
4. Record state transitions using UTC timestamps.
5. Maintain audit records of successful tool executions.
6. Introduce a configurable tool execution limit.
7. Enforce the execution limit before tool invocation.
8. Handle successful, failed, and no-tool-selected investigations.
9. Preserve compatibility with existing security detection and investigation components.
10. Validate the implementation using automated tests.

---

## 3. Lab Environment and Technology Stack

### 3.1 Development Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Programming language | Python 3.13.17 |
| Development environment | Visual Studio Code |
| Terminal | PowerShell |
| Virtual environment | Python `.venv` |
| Testing framework | Pytest 9.2.0 |
| Local AI runtime | Ollama |
| Language model | Qwen3 4B (`qwen3:4b`) |
| Security datasets | Synthetic authentication and AWS CloudTrail JSON |
| Version control | Git and GitHub |

### 3.2 Key Python Modules

| Module | Function |
|---|---|
| `src/detector.py` | Authentication brute-force detection |
| `src/cloudtrail_parser.py` | CloudTrail authentication event normalization |
| `src/iam_parser.py` | IAM event parsing |
| `src/iam_detector.py` | IAM security detection |
| `src/agents/investigator.py` | Deterministic and optional AI-assisted investigation |
| `src/agents/llm_client.py` | Local LLM security analysis |
| `src/agents/investigation_tools.py` | Read-only CloudTrail evidence lookup |
| `src/agents/tool_registry.py` | Approved investigation tool registry |
| `src/agents/tool_selector.py` | AI-assisted tool selection |
| `src/agents/tool_executor.py` | Controlled tool execution |
| `src/agents/agentic_workflow.py` | Agentic investigation orchestration |
| `src/agents/investigation_state.py` | Investigation state and audit management |

### 3.3 Dataset Description

The project uses synthetic security datasets to simulate cloud security events.

The authentication dataset includes examples of successful and failed login attempts. A synthetic CloudTrail dataset contains six `ConsoleLogin` events, including five failed authentication attempts from the same source IP address.

The IAM dataset contains two simulated `CreateAccessKey` operations: an administrative event and a self-service access key creation event.

These datasets support reproducible testing without requiring access to real AWS infrastructure or sensitive production records.

---

## 4. System Architecture

### 4.1 Architecture Overview

SentinelAI separates security event processing, detection logic, AI-assisted tool selection, and investigation management into modular components.

The Day 9 architecture adds investigation state tracking and audit recording to the existing workflow.

**Investigation workflow:**

```text
          Synthetic Security Events
                    |
                    v
             Security Parsers
                    |
                    v
             Detection Engines
                    |
                    v
            Structured Security Alert
                    |
                    v
          Initialize Investigation State
                    |
                    v
             Local Qwen3 Model
                    |
                    v
           Approved Tool Selection
                    |
                    v
          Validate Execution Limit
                    |
                    v
          Controlled Tool Executor
                    |
                    v
          Read-Only Evidence Lookup
                    |
                    v
           Record Tool Execution
                    |
                    v
           Update Investigation State
                    |
                    v
          Investigation Result & Audit Log
                    |
                    v
              Analyst Review
```

### 4.2 Architectural Design Principles

The implementation follows several important principles:

- **Modularity:** Detection, investigation, AI inference, and state management are implemented in separate modules.
- **Controlled execution:** The AI can recommend tools only from an approved registry.
- **Read-only investigation:** The existing approved tool retrieves local security evidence without modifying cloud resources.
- **Auditability:** Investigation transitions and successful tool executions are recorded.
- **Human oversight:** AI-generated findings remain advisory.
- **Local-first operation:** The prototype does not depend on deployed AWS infrastructure or paid AI services.

The current implementation supports a single AI-selected tool call per investigation. Iterative agent planning and multi-step orchestration remain future development objectives.

---

## 5. Methodology and Implementation

### 5.1 Step 1 — Investigation State Initialization

**Objective:** Create a structured state object to maintain investigation information.

A new module was created:

`src/agents/investigation_state.py`

The module introduces the function:

`create_investigation_state(alert)`

This function accepts a security alert and creates an initial investigation record.

The state contains the following fields:

| Field | Description |
|---|---|
| `investigation_id` | Unique UUID assigned to the investigation |
| `alert` | Original security alert |
| `status` | Current investigation status |
| `current_step` | Current workflow stage |
| `tool_executions` | Recorded successful tool executions |
| `audit_log` | Investigation activity history |
| `max_tool_calls` | Maximum permitted recorded tool calls |
| `tool_calls_used` | Number of successful executions recorded |
| `created_at` | UTC investigation creation timestamp |
| `completed_at` | UTC completion timestamp, initially null |

The function uses Python's `uuid` module to generate unique identifiers and the `datetime` module to record UTC timestamps.

**Verification:** A sample brute-force alert was passed to the initialization function. The resulting JSON contained an investigation identifier, an `initialized` status, empty execution and audit lists, and a zero tool-call count.

**Result:** Investigation state initialization completed successfully.

### 5.2 Step 2 — Investigation State Transitions

**Objective:** Track changes in investigation progress.

The function `update_investigation_state()` was added to manage status updates.

Supported statuses include:

- `initialized`
- `selecting_tool`
- `executing_tool`
- `completed`
- `failed`

The function validates the requested status and prevents further updates after an investigation reaches a terminal state.

Each transition produces an audit record containing the timestamp, previous status, new status, and workflow step.

**Example transition:**

```text
Previous status: initialized
New status: selecting_tool
Current step: tool_selection
Audit entries: 1
```

When an investigation reaches `completed` or `failed`, the function also records a completion timestamp.

**Result:** State transitions and audit logging were successfully verified.

### 5.3 Step 3 — Tool Execution Recording

**Objective:** Maintain an auditable history of successful investigation tool executions.

The function `record_tool_execution()` was implemented.

It validates the execution record, checks the current investigation state, and verifies that the configured tool-call limit has not been reached.

A valid execution record contains:

```python
{
    "tool_name": "lookup_login_activity",
    "parameters": {
        "source_ip": "198.51.100.50"
    },
    "result": {
        "count": 5
    },
    "status": "success"
}
```

After a successful record is accepted, the function:

1. Adds a timestamped entry to `tool_executions`.
2. Increments `tool_calls_used`.
3. Adds a corresponding tool execution event to `audit_log`.

The function currently records successful tool executions rather than all attempted executions.

**Result:** Tool execution recording and audit entry generation were verified.

### 5.4 Step 4 — Tool Execution Limit Validation

**Objective:** Prevent an investigation from recording more tool executions than permitted.

The initial state configuration sets:

```python
"max_tool_calls": 1,
"tool_calls_used": 0
```

A validation exercise attempted to record the same execution twice.

The first record was accepted. The second attempt raised a `RuntimeError`.

**Observed terminal output:**

```text
PASS: Second execution was rejected.
Reason: Investigation tool execution limit reached.
Tool calls recorded: 1
Execution records: 1
```

This confirmed that the state recorder rejects additional successful execution records after reaching the configured limit.

The execution limit was subsequently checked before tool invocation in the integrated workflow.

**Result:** Execution limit validation passed.

### 5.5 Step 5 — Integration with the Agentic Investigation Workflow

**Objective:** Integrate state management into the existing Day 8 agentic workflow.

The existing file was updated:

`src/agents/agentic_workflow.py`

The updated workflow performs the following operations:

1. Initializes an investigation state.
2. Updates the status to `selecting_tool`.
3. Requests a tool recommendation from the local AI selector.
4. Completes the investigation if no tool is selected.
5. Checks the tool execution limit before invoking a selected tool.
6. Updates the status to `executing_tool`.
7. Executes the approved read-only investigation tool.
8. Records the successful execution and audit event.
9. Updates the investigation status to `completed`.
10. Returns the investigation result with its associated state.

If an exception occurs, the workflow records an error event and transitions the investigation to `failed`.

The integration preserves the existing result fields and adds an `investigation_state` field.

**Result:** State management was successfully integrated into the agentic workflow.

### 5.6 Step 6 — Existing Test Compatibility

After integrating the new state management module, the existing test suite was executed.

**Initial result:** 24 tests passed and one test failed.

The failure occurred because a mocked tool execution result in `tests/test_agentic_workflow.py` did not include the `parameters` field required by the new execution recorder.

The test fixture was updated to match the actual tool executor's expected response structure.

**Subsequent result:** All 25 existing tests passed.

This demonstrated compatibility between the updated workflow and the previously implemented detection and investigation components.

### 5.7 Step 7 — Automated Investigation State Testing

A new test file was created:

`tests/test_investigation_state.py`

Six automated tests were implemented.

| Test | Purpose | Result |
|---|---|---|
| Investigation initialization | Validate initial state fields | Passed |
| State transition | Validate status changes and audit entries | Passed |
| Invalid status rejection | Reject unsupported statuses | Passed |
| Execution recording | Verify execution and audit records | Passed |
| Execution limit enforcement | Reject a second execution record | Passed |
| Completed-state protection | Prevent changes after completion | Passed |

**Observed result:**

```text
6 passed in 0.07s
```

### 5.8 Step 8 — Agentic Workflow Audit Testing

Additional tests were introduced in `tests/test_agentic_workflow.py`.

These tests verify three important investigation scenarios.

**Scenario A: Successful investigation**

A mocked AI selector chooses `lookup_login_activity`, and the mocked executor returns a successful result.

The test confirms that the investigation completes, one execution is recorded, and the audit history includes the expected status transitions.

**Scenario B: Tool execution failure**

A simulated `RuntimeError` is raised during evidence retrieval.

The workflow records an error event, transitions to `failed`, and preserves the investigation identifier and completion timestamp.

**Scenario C: No tool selected**

The AI selector returns no tool.

The workflow completes without invoking the executor, records the completion transition, and maintains a tool-call count of zero.

**Observed result:**

```text
5 passed in 0.40s
```

These tests use mocked dependencies and do not require live LLM inference.

---

## 6. Testing and Results

### 6.1 Final Automated Test Results

The complete SentinelAI test suite was executed using:

```powershell
python -m pytest -v
```

**Observed terminal result:**

```text
collected 34 items

34 passed in 0.50s
```

### 6.2 Test Coverage Summary

| Component | Number of Tests | Result |
|---|---:|---|
| Authentication detection | 10 | Passed |
| IAM security detection | 2 | Passed |
| Investigation state management | 6 | Passed |
| Deterministic and AI-assisted investigator | 2 | Passed |
| Local LLM client | 1 | Passed |
| Controlled tool executor | 4 | Passed |
| AI tool selector | 4 | Passed |
| Agentic investigation workflow | 5 | Passed |
| **Total** | **34** | **All passed** |

### 6.3 Key Findings

The testing confirmed that:

- Investigations can be assigned unique identifiers.
- State transitions are recorded with timestamps.
- Successful tool executions generate structured audit entries.
- The configured execution record limit is enforced.
- The integrated workflow checks the limit before tool invocation.
- Completed investigations reject subsequent state updates.
- Simulated tool failures produce structured failed investigation results.
- No-tool-selected investigations finish without invoking an executor.
- Existing authentication, IAM, and AI-related tests remain functional.

### 6.4 Evaluation Limitations

The automated tests validate defined behavior using synthetic inputs and mocked dependencies.

They do not establish production readiness, comprehensive security coverage, or reliable LLM behavior under adversarial conditions.

The Day 9 validation primarily exercised deterministic state management and mocked workflow interactions. The supplied results do not establish a new end-to-end Day 9 investigation run using live local Qwen3 inference.

---

## 7. Security Considerations

### 7.1 Tool Allowlisting

The existing tool registry restricts execution to explicitly approved investigation functions.

This reduces the possibility of an AI-generated recommendation directly invoking an arbitrary function.

However, registry metadata alone does not provide independent operating-system-level isolation.

### 7.2 Input Validation

The Day 8 implementation validates selected tool names and parameter structures.

For source-IP lookups, the final execution target is derived from the original alert rather than relying on the LLM's reproduced IP address.

This safeguard addresses an observed local-model transcription error.

### 7.3 Investigation Auditability

Day 9 improves traceability by recording investigation identifiers, state transitions, successful execution details, and error types.

These records provide a foundation for future analyst review and troubleshooting.

The audit log is currently an in-memory application structure, not an independently protected or persistent security audit system.

### 7.4 Execution Limits

The current workflow checks the tool-call limit before invoking an approved tool.

However, the counter increments after successful execution recording. Failed attempts are not counted in the same way.

Additional controls would be required before introducing retries, concurrent execution, or multi-step agent loops.

### 7.5 Human Oversight

The platform does not automatically block users, revoke IAM credentials, or modify AWS infrastructure.

AI-generated analysis and investigation findings remain advisory and require human validation.

---

## 8. Challenges Encountered and Resolutions

| Challenge | Cause | Resolution |
|---|---|---|
| Existing workflow test failed | Mock execution lacked required `parameters` field | Updated the test fixture to match the executor response |
| Need for investigation traceability | Original workflow returned results without detailed lifecycle history | Added investigation state and audit logging |
| Risk of uncontrolled tool execution | No explicit workflow-level pre-execution limit | Added a limit check before tool invocation |
| Handling investigation errors | Tool failures required structured reporting | Added failed-state handling and error audit entries |
| Avoiding unnecessary tool calls | Some investigations may not require evidence lookup | Added an auditable no-tool completion path |

These changes improved the structure and testability of SentinelAI without introducing live cloud operations.

---

## 9. Development Progress Summary

| Development Day | Major Accomplishment | Status |
|---|---|---|
| Day 1 | Python environment, authentication ingestion, brute-force detection | Completed |
| Day 2 | Synthetic detection evaluation and confusion matrix | Completed |
| Day 3 | Initial automated detection tests | Completed |
| Day 4 | Detection reliability and input handling improvements | Completed |
| Day 5 | Synthetic AWS CloudTrail authentication integration | Completed |
| Day 6 | IAM detection and deterministic SOC investigation | Completed |
| Day 7 | Local Qwen3 integration through Ollama | Completed |
| Day 8 | Controlled AI tool selection and read-only execution | Completed |
| Day 9 | Investigation state management, audit logging, and stopping conditions | Implemented and tested |

Day 8 was committed and published to GitHub. Day 9 changes have been validated locally but have not yet been committed or published.

---

## 10. Future Improvements

The next development phases can extend SentinelAI in several areas.

**Investigation orchestration:** Introduce more explicit transition rules, multi-step investigation states, and controlled evidence correlation using a framework such as LangGraph.

**Auditability:** Add persistent, structured investigation logs with stronger evidence provenance and safeguards against modification.

**Execution safety:** Track tool attempts as well as successful executions, introduce timeout handling, and strengthen controls for retries and failures.

**Security evaluation:** Test prompt-injection scenarios, unsupported LLM conclusions, malformed tool outputs, and adversarial security events.

**SOC visualization:** Develop a Streamlit dashboard for security alerts, investigation progress, evidence, and analyst review.

**Continuous integration:** Introduce GitHub Actions to execute automated tests when repository changes are submitted.

All future functionality should preserve the project's local-first approach, read-only investigation principles, and human oversight requirements.

---

## 11. Conclusion

Day 9 successfully extended SentinelAI's agentic investigation capabilities through structured state management and audit logging.

The implementation introduced unique investigation identifiers, lifecycle status tracking, execution records, timestamped audit entries, execution limit checks, and structured failure handling.

Automated validation confirmed that the new components work alongside the existing authentication detection, IAM monitoring, local LLM integration, and controlled tool execution modules.

**The final test suite completed with 34 passing tests and zero failures.**

The results demonstrate progress toward a more transparent and controlled AI-assisted SOC investigation platform. Although SentinelAI remains a local research prototype, its modular architecture and growing automated test suite provide a foundation for future stateful agent orchestration, security evaluation, and analyst-facing capabilities.

---

## 12. Project Repository

**GitHub:** https://github.com/Nj2310/sentinelai-agentic-cloud-soc

**Latest published phase:** Day 8  
**Current locally validated phase:** Day 9

---

## 13. Disclaimer

SentinelAI is an educational cybersecurity research and portfolio development project.

All described security events and datasets are synthetic. The platform is not intended for production security monitoring, automated incident response, or autonomous cloud remediation.

The reported test results validate specific implementation behaviors and should not be interpreted as evidence of real-world detection accuracy, operational resilience, or production security readiness.

Any future operational deployment would require additional security testing, independent validation, appropriate access controls, and human oversight.