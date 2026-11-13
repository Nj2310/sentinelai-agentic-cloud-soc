# SentinelAI — Agentic AI Cloud Security Operations Platform

## Technical Lab Report: Investigation State Management, Auditability, and Execution Safety

**Project:** SentinelAI — Agentic AI Cloud Security Operations Platform  
**Development Phase:** Day 10
**Project Type:** Cybersecurity Research and Development  
**Environment:** Python 3.13.17, Windows, Visual Studio Code  
**Technologies:** Python, AWS CloudTrail (Synthetic), Ollama, Qwen3 4B, Pytest  
**Development Approach:** Local-First, AI-Assisted Security Operations  
**Project Status:** Day 10 implementation validated locally — 36 automated tests passed

---

## 1. Executive Summary

SentinelAI is a local-first cybersecurity research project designed to explore how artificial intelligence can support Security Operations Center (SOC) investigations through security event detection, automated evidence collection, and controlled investigation workflows.

The platform combines Python-based detection engineering, synthetic AWS CloudTrail analysis, Identity and Access Management (IAM) monitoring, and a locally hosted Qwen3 4B language model through Ollama.

During the earlier development phases, SentinelAI progressed from basic authentication brute-force detection to IAM security monitoring, deterministic SOC investigation, AI-assisted analysis, and controlled AI-directed tool execution.


**Day 9 introduced investigation state management and auditability. Day 10 strengthened investigation execution safety by implementing tool-attempt tracking, stricter state-transition validation, and improved audit coverage.**

The updated workflow records tool attempts before execution, ensuring that failed tool executions still count toward the investigation's configured attempt limit. State transitions are validated against an explicit set of permitted transitions, preventing invalid investigation lifecycle changes.

These improvements maintain SentinelAI's controlled, read-only investigation design while providing clearer visibility into tool usage and investigation failures.

The implementation was validated using automated tests covering investigation initialization, state transitions, execution recording, stopping conditions, successful investigations, and failure scenarios.

**Final validation result: 36 automated tests passed, with zero failures.**

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

The purpose of Day 10 was to strengthen SentinelAI's existing agentic investigation workflow by improving execution safety, tool-attempt accountability, and investigation state-transition validation.

Day 9 established the foundation for structured investigation state management, unique investigation identifiers, lifecycle tracking, audit logging, and execution limits.

Day 10 extended these capabilities by introducing explicit tool-attempt tracking before execution, ensuring that failed tool executions count toward the configured attempt limit.

The implementation also strengthened investigation lifecycle controls by validating state transitions against explicitly permitted paths and rejecting invalid transitions without modifying the investigation state or recording a successful transition.

Together, these improvements enhance the transparency, predictability, and accountability of SentinelAI's controlled, read-only AI-assisted investigation workflow.

The implementation remains a local-first cybersecurity research prototype using synthetic security data and application-level execution controls.

### 2.3 Lab Objectives

The primary objectives of Day 10 were to:

1. Extend the existing Day 9 investigation state management framework.
2. Introduce a dedicated `tool_attempts` counter to track attempted tool executions.
3. Maintain separate counters for attempted and successfully recorded tool executions.
4. Record tool invocation attempts before execution begins.
5. Ensure failed tool executions count toward the configured execution-attempt limit.
6. Enforce a maximum of one tool attempt per investigation in the current workflow.
7. Validate investigation state transitions against explicitly permitted lifecycle paths.
8. Reject invalid state transitions without modifying the investigation status or recording a successful transition.
9. Preserve structured audit records for investigation transitions, tool attempts, successful executions, and errors.
10. Maintain compatibility with existing authentication detection, IAM monitoring, and AI-assisted investigation components.
11. Validate the strengthened investigation workflow using automated tests.
12. Confirm that all 36 automated tests pass without failures.

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

SentinelAI separates security event processing, detection engineering, AI-assisted investigation, controlled tool execution, and investigation state management into modular Python components.

The current architecture incorporates the Day 9 investigation state and audit logging capabilities alongside Day 10 tool-attempt tracking, execution-limit enforcement, and strict state-transition validation.

**Implemented Investigation Workflow:**

```text
           Synthetic Security Events
          (Authentication / CloudTrail)
                       |
                       v
                Security Parsers
                       |
                       v
                Detection Engines
           (Brute-Force / IAM Activity)
                       |
                       v
             Structured Security Alert
                       |
                       v
           Initialize Investigation State
                  (initialized)
                       |
                       v
             AI-Assisted Tool Selection
                 (selecting_tool)
                       |
               +-------+-------+
               |               |
          No Tool Selected  Tool Selected
               |               |
               v               v
           completed      Validate Tool Name,
                          Parameters and Limit
                               |
                               v
                         executing_tool
                               |
                               v
                       Record Tool Attempt
                       (before execution)
                               |
                               v
                       Controlled Executor
                               |
                               v
                       Read-Only Evidence
                             Lookup
                               |
                       +-------+-------+
                       |               |
                    Success          Failure
                       |               |
                       v               v
                Record Successful    Record Error
                Tool Execution       in Audit Log
                       |               |
                       v               v
                   completed         failed
                       |               |
                       +-------+-------+
                               |
                               v
                   Investigation Result
                     + In-Memory Audit
                               |
                               v
                         Analyst Review
```

**Investigation State Transitions:**

| Current State | Permitted Next States |
|---|---|
| `initialized` | `selecting_tool`, `failed` |
| `selecting_tool` | `executing_tool`, `completed`, `failed` |
| `executing_tool` | `completed`, `failed` |
| `completed` | None (terminal) |
| `failed` | None (terminal) |

**Day 10 Execution Safety Controls:**

- Tool attempts are recorded before execution.
- Failed tool executions count toward the configured attempt limit.
- The workflow currently permits a maximum of one tool attempt per investigation.
- Tool names and parameters are validated before execution.
- Invalid investigation state transitions are rejected.
- Investigation audit records are maintained in memory.
- AI-generated findings remain advisory; no autonomous remediation is performed.

**Implementation Scope:** SentinelAI currently operates locally using synthetic security data and a locally hosted Qwen3 model through Ollama. Live AWS integration, production SIEM connectivity, and multi-step autonomous orchestration are not yet implemented.

### 4.2 Architectural Design Principles

The implementation follows several important principles:

- **Modularity:** Detection, investigation, AI inference, and state management are implemented in separate modules.
- **Controlled execution:** The AI can recommend tools only from an approved registry.
- **Read-only investigation:** The existing approved tool retrieves local security evidence without modifying cloud resources.
- **Auditability:** Investigation state transitions, tool invocation attempts, successful tool executions, and investigation errors are recorded in an in-memory audit log. Day 10 ensures that failed tool executions remain traceable through pre-execution attempt records.
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
| `audit_log` | In-memory investigation activity history |
| `max_tool_calls` | Maximum permitted tool attempts per investigation |
| `tool_attempts` | Number of recorded tool attempts, including failed executions |
| `tool_calls_used` | Number of successfully recorded tool executions |
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

1. Initializes an investigation state with a unique investigation identifier.
2. Updates the investigation status to `selecting_tool`.
3. Requests a tool recommendation from the local AI selector.
4. Completes the investigation if no tool is selected.
5. Validates the selected tool, its parameters, and the configured execution-attempt limit.
6. Updates the investigation status to `executing_tool`.
7. Calls `record_tool_attempt()` to record the attempt and increment `tool_attempts` before execution.
8. Executes the approved read-only investigation tool.
9. Records successful tool execution details and increments `tool_calls_used` when execution succeeds.
10. Updates the investigation status to `completed` after successful execution.
11. Returns the investigation result with its associated investigation state and audit history.

If an exception occurs, the workflow records an error event and transitions the investigation to `failed`. A failed tool execution still counts toward `tool_attempts` because the attempt was recorded before execution began.

The integration preserves the existing investigation result fields and adds an `investigation_state` field containing lifecycle information, execution counters, and audit records.

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


### 5.9 Step 9 — Tool-Attempt Tracking and Execution Safety (Day 10)

Day 10 introduced additional execution-safety controls to the SentinelAI investigation workflow.

**Objective:** Ensure that every tool invocation attempt is counted, including attempts that fail during execution.

**Implementation:**

The investigation state now maintains two separate counters:

- `tool_attempts`: Number of recorded tool invocation attempts, including failed executions.
- `tool_calls_used`: Number of successfully recorded tool executions.

The `record_tool_attempt()` function was introduced in `src/agents/investigation_state.py`.

Before executing an approved investigation tool, the workflow records the attempt and increments `tool_attempts`.

The function also creates an audit entry containing:

- UTC timestamp
- Event type (`tool_attempt`)
- Selected tool name
- Attempt number

The workflow enforces the configured `max_tool_calls` limit against `tool_attempts`, preventing failed executions from bypassing the attempt limit.

**Security significance:**

This control improves accountability and helps prevent repeated tool execution attempts within a single investigation.

The current workflow remains limited to one tool attempt per investigation and does not perform autonomous remediation.


### 5.10 Step 10 — Strict Investigation State-Transition Validation (Day 10)

Day 10 introduced explicit state-transition validation to prevent investigations from moving through invalid lifecycle sequences.

**Objective:** Ensure that investigation status changes follow a controlled and predictable workflow.

**Implementation:**

The `update_investigation_state()` function in `src/agents/investigation_state.py` now validates requested transitions against an explicit transition table.

The permitted transitions are:

| Current State | Permitted Next States |
|---|---|
| `initialized` | `selecting_tool`, `failed` |
| `selecting_tool` | `executing_tool`, `completed`, `failed` |
| `executing_tool` | `completed`, `failed` |
| `completed` | None |
| `failed` | None |

Invalid transitions raise a `ValueError` without changing the investigation status or adding a transition audit entry.

For example, an investigation cannot transition directly from `initialized` to `executing_tool` because tool selection must occur first.

The `completed` and `failed` states are terminal, preventing further state updates.

**Security significance:**

Explicit state-transition validation improves workflow consistency, reduces unintended execution paths, and strengthens investigation lifecycle controls.

The implementation enforces application-level workflow rules; it is not a replacement for operating-system isolation or external security controls.

## 6. Testing and Results

### 6.1 Final Automated Test Results

The complete SentinelAI test suite was executed using:

```powershell
python -m pytest -v
```

**Observed terminal result:**

```text
collected 36 items

36 passed in 0.46s
```

### 6.2 Test Coverage Summary

| Component | Number of Tests | Result |
|---|---:|---|
| Authentication detection | 10 | Passed |
| IAM security detection | 2 | Passed |
| Investigation state management | 8 | Passed |
| Deterministic and AI-assisted investigator | 2 | Passed |
| Local LLM client | 1 | Passed |
| Controlled tool executor | 4 | Passed |
| AI tool selector | 4 | Passed |
| Agentic investigation workflow | 5 | Passed |
| **Total** | **36** | **All passed** |

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


**Additional Day 10 findings:**

- Tool invocation attempts are recorded before execution.
- Failed tool executions count toward the configured attempt limit.
- The workflow tracks attempted and successfully recorded tool executions separately.
- A second tool attempt is rejected when the configured attempt limit has been reached.
- Invalid investigation state transitions are rejected without modifying the investigation status or recording a successful transition.
- Completed and failed investigations are treated as terminal states.
- The existing agentic workflow tests remain compatible with the strengthened execution controls.

The complete Day 10 automated test suite passed all 36 tests with zero failures.

### 6.4 Evaluation Limitations

The automated tests validate defined behavior using synthetic inputs and mocked dependencies.

They do not establish production readiness, comprehensive security coverage, or reliable LLM behavior under adversarial conditions.

The Day 9 validation primarily exercised deterministic state management and mocked workflow interactions. The supplied results do not establish a new end-to-end Day 9 investigation run using live local Qwen3 inference.


**Day 10 evaluation limitations:**

The Day 10 automated tests validate tool-attempt accounting, execution-limit enforcement, and investigation state-transition rules using controlled test scenarios.

These controls operate at the Python application level. The read-only tool registry represents an application policy boundary, not an operating-system sandbox.

Investigation state and audit records are maintained in memory. They are not currently persisted to an external audit store or protected against tampering.

The workflow currently supports a maximum of one tool attempt per investigation. Multi-step autonomous orchestration, production SIEM integration, and automated incident remediation have not yet been implemented.

The successful execution of 36 automated tests demonstrates correctness for the tested scenarios but does not establish production readiness or comprehensive security coverage.

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

Day 9 introduced investigation identifiers, lifecycle state tracking, execution records, and structured audit entries.

Day 10 expanded audit coverage by recording tool invocation attempts before execution.

The investigation audit log now records:

- Investigation state transitions with UTC timestamps.
- Tool invocation attempts, including the selected tool name and attempt number.
- Successful tool execution records.
- Investigation errors, including the exception type.

Failed tool executions are reflected through their recorded attempt and subsequent investigation failure.

These records improve traceability and support future security analyst review and troubleshooting.

**Current limitation:** Audit records are stored in memory and are not yet persisted to a tamper-resistant external logging system.

### 7.4 Execution Limits

Day 10 strengthened execution-limit enforcement by introducing explicit tool-attempt tracking.

The investigation state maintains two counters:

- `tool_attempts`: Tracks tool invocation attempts, including failed executions.
- `tool_calls_used`: Tracks successfully recorded tool executions.

Before invoking an approved tool, the agentic workflow calls `record_tool_attempt()`.

This function increments the attempt counter and records an audit event before execution begins.

The workflow enforces the configured `max_tool_calls` limit against `tool_attempts`, ensuring that failed executions cannot bypass the configured attempt limit.

The current investigation workflow permits a maximum of one tool attempt per investigation.

These controls provide application-level execution safeguards. Additional protections would be necessary before supporting concurrent investigations, automated retries, or multi-step autonomous agent workflows.

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
| Day 9 | Investigation state management, audit logging, and stopping conditions | Completed and published |
| Day 10 | Tool-attempt tracking, execution-limit enforcement, strict state transitions, and 36 passing tests | Completed and published |

**Day 10 Status:** Completed, tested, and published to GitHub.

**Day 10 Key Achievements:**
- Implemented tool-attempt tracking before execution.
- Enforced a maximum of one tool attempt per investigation.
- Ensured failed tool executions count toward the configured attempt limit.
- Implemented strict investigation state-transition validation.
- Improved investigation auditability and execution safety.
- Successfully validated the implementation with 36 passing automated tests.

**GitHub Commit:** `21d0f90`

Days 1–10 have been implemented, tested, and published to GitHub. Day 10 strengthens SentinelAI's agentic investigation workflow through execution-safety controls, auditable tool attempts, and validated state transitions.

---

## 10. Future Improvements

The next development phases can extend SentinelAI in several areas.

**Investigation orchestration:** Extend the existing state-transition validation to support controlled multi-step investigations, evidence correlation across multiple security events, and more advanced workflow orchestration. A framework such as LangGraph may be evaluated in a future development phase. The current implementation supports one approved tool attempt per investigation.

**Auditability:** Add persistent, structured investigation logs with stronger evidence provenance and safeguards against modification.

**Execution safety:** Extend the existing Day 10 tool-attempt tracking and execution-limit controls with timeout handling, stronger failure recovery, controlled retry policies, and safeguards for concurrent investigations. Any future expansion beyond the current single-attempt workflow must preserve strict state-transition validation and prevent failed tool executions from bypassing configured limits.

**Security evaluation:** Test prompt-injection scenarios, unsupported LLM conclusions, malformed tool outputs, and adversarial security events.

**SOC visualization:** Develop a Streamlit dashboard for security alerts, investigation progress, evidence, and analyst review.

**Continuous integration:** Introduce GitHub Actions to execute automated tests when repository changes are submitted.

All future functionality should preserve the project's local-first approach, read-only investigation principles, and human oversight requirements.

---

## 11. Conclusion

Day 10 successfully strengthened SentinelAI's agentic investigation workflow through tool-attempt tracking, execution-limit enforcement, strict state-transition validation, and improved auditability.

Building on Day 9's investigation state management, the Day 10 implementation introduced separate tracking for attempted and successfully recorded tool executions. Failed tool executions now count toward the configured attempt limit, preventing repeated execution attempts from bypassing workflow restrictions.

The investigation lifecycle now enforces explicit permitted state transitions, rejecting invalid transitions and protecting completed or failed investigations from further updates.

SentinelAI continues to integrate Python-based authentication detection, synthetic AWS CloudTrail and IAM security monitoring, deterministic SOC investigation, and optional AI-assisted analysis using a locally hosted Qwen3 4B model through Ollama.

**Final validation result: 36 automated tests passed, with zero failures.**

The implementation remains a local-first cybersecurity research prototype using synthetic security data. Investigation tools are restricted through application-level controls, audit records are maintained in memory, and AI-generated findings remain advisory.

Future development will focus on expanded evidence correlation, controlled multi-step investigations, stronger security evaluation, persistent audit logging, and analyst-facing visualization.

**Day 10 development, automated testing, documentation, and GitHub publication have been completed successfully.**
---

## 12. Project Repository

**GitHub:** https://github.com/Nj2310/sentinelai-agentic-cloud-soc

**Latest published phase:** Day 10

**Current development status:** Day 10 completed, tested, and published to GitHub

**Automated test results:** 36 tests passed, zero failures

**Latest Day 10 commit:** `21d0f90`

**Project maturity:** Local-first cybersecurity research prototype using synthetic security data

---

## 13. Disclaimer

SentinelAI is an educational cybersecurity research and portfolio development project.

All described security events and datasets are synthetic. The platform is not intended for production security monitoring, automated incident response, or autonomous cloud remediation.

The reported test results validate specific implementation behaviors and should not be interpreted as evidence of real-world detection accuracy, operational resilience, or production security readiness.

Any future operational deployment would require additional security testing, independent validation, appropriate access controls, and human oversight.
