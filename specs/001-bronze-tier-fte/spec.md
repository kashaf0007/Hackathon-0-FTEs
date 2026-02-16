# Feature Specification: Bronze Tier Constitutional FTE

**Feature Branch**: `001-bronze-tier-fte`
**Created**: 2026-02-16
**Status**: Draft
**Input**: User description: "Bronze Tier Constitutional FTE - Minimum Viable Constitutional FTE with Local-First, HITL, Proactivity, Persistence, Transparency, and Cost Efficiency principles"

## User Scenarios & Testing

### User Story 1 - Autonomous Task Execution with Safety Guardrails (Priority: P1)

A developer wants the Digital FTE to autonomously execute routine tasks (like drafting emails, creating reports, organizing files) while ensuring that any high-risk actions require explicit human approval before execution.

**Why this priority**: This is the core value proposition of a Bronze Tier FTE - structured autonomy with safety boundaries. Without this, the system is just a manual assistant.

**Independent Test**: Can be fully tested by triggering a task that requires approval (e.g., file deletion request) and verifying that the system creates a pending approval file, blocks execution, and only proceeds after manual approval.

**Acceptance Scenarios**:

1. **Given** a low-risk task is detected in /Needs_Action/, **When** the Task Orchestrator processes it, **Then** the task executes automatically and logs the action
2. **Given** a high-risk task is detected (e.g., delete files, send external emails), **When** the Approval Guard evaluates it, **Then** a file is created in /Pending_Approval/ and execution is blocked
3. **Given** an approval file exists in /Pending_Approval/, **When** a human manually approves it, **Then** the task executes and the file moves to /Done/
4. **Given** a task completes successfully, **When** the system finishes all steps, **Then** the task file moves to /Done/ and a completion marker is logged

---

### User Story 2 - Complete Transparency Through Audit Logging (Priority: P1)

A compliance officer or developer needs to review all actions taken by the Digital FTE to ensure accountability, debug issues, and verify constitutional compliance.

**Why this priority**: Transparency is a core constitutional principle. Without comprehensive logging, the system cannot be trusted or debugged effectively.

**Independent Test**: Can be fully tested by triggering various actions (low-risk, high-risk, approved, rejected) and verifying that all actions appear in /Logs/YYYY-MM-DD.json with complete metadata (timestamp, action, skill, risk level, approval status).

**Acceptance Scenarios**:

1. **Given** any action is performed by the FTE, **When** the action completes, **Then** an entry is logged in /Logs/YYYY-MM-DD.json with timestamp, action description, skill used, and risk classification
2. **Given** a high-risk action requires approval, **When** the approval is granted or denied, **Then** the approval decision is logged with the approver identity
3. **Given** a constitutional violation is detected, **When** the logging system processes it, **Then** the violation is flagged in the log with details
4. **Given** a user wants to audit actions, **When** they review the daily log file, **Then** they can trace the complete execution history with all relevant metadata

---

### User Story 3 - Proactive Task Detection and Queueing (Priority: P2)

A user wants the Digital FTE to proactively monitor for new work (emails, file changes, scheduled tasks) and automatically queue tasks for processing without manual intervention.

**Why this priority**: Proactivity distinguishes an autonomous FTE from a reactive assistant. This enables true "set it and forget it" operation.

**Independent Test**: Can be fully tested by setting up a watcher (e.g., email monitor), triggering an event (sending an email), and verifying that a task file is automatically created in /Needs_Action/.

**Acceptance Scenarios**:

1. **Given** a watcher system is configured, **When** a triggering event occurs (new email, file change, scheduled time), **Then** a task file is created in /Needs_Action/
2. **Given** multiple events occur simultaneously, **When** the watcher processes them, **Then** each event creates a separate task file with unique identifiers
3. **Given** a task file is created in /Needs_Action/, **When** the Task Orchestrator detects it, **Then** the task is picked up and processed according to its priority

---

### User Story 4 - Persistent Task Execution (Ralph Wiggum Principle) (Priority: P2)

A developer wants the Digital FTE to continue working on tasks until they are genuinely complete, not giving up on first failure or partial completion.

**Why this priority**: Persistence ensures reliability and reduces manual intervention. Without this, the FTE would require constant supervision.

**Independent Test**: Can be fully tested by creating a multi-step task, simulating a failure in step 2, and verifying that the system retries or requests help rather than abandoning the task.

**Acceptance Scenarios**:

1. **Given** a multi-step task is in progress, **When** a step fails, **Then** the system logs the failure and either retries or creates a help request in /Needs_Action/
2. **Given** a task is partially complete, **When** the system evaluates completion status, **Then** it continues processing until the task file moves to /Done/ or emits `<promise>TASK_COMPLETE</promise>`
3. **Given** a task encounters a blocker, **When** the system cannot proceed, **Then** it creates a clear status update and waits for human intervention rather than silently failing

---

### User Story 5 - Structured Skill Management (Priority: P3)

A developer wants to add, modify, or understand the capabilities of the Digital FTE by reviewing structured skill definitions in a standardized format.

**Why this priority**: While important for maintainability, this is primarily a developer experience feature that doesn't directly impact end-user value.

**Independent Test**: Can be fully tested by reading a skill definition from .claude/skills/[skill-name]/SKILL.md and verifying it contains all required sections (Purpose, Constitutional Alignment, Inputs, Outputs, Risk Classification, etc.).

**Acceptance Scenarios**:

1. **Given** a new skill needs to be added, **When** a developer creates a SKILL.md file following the schema, **Then** the FTE can load and execute the skill
2. **Given** a skill definition exists, **When** a developer reviews it, **Then** they can understand the skill's purpose, inputs, outputs, risk level, and execution logic without reading code
3. **Given** multiple skills exist, **When** the FTE needs to select a skill for a task, **Then** it can evaluate which skill to use based on the structured metadata

---

### Edge Cases

- What happens when /Logs/ directory doesn't exist or is not writable?
- How does the system handle a task that requires approval but the approval file is manually deleted?
- What happens when a task loops indefinitely without reaching completion?
- How does the system handle concurrent tasks that conflict (e.g., both trying to modify the same file)?
- What happens when .env file is missing or contains invalid credentials?
- How does the system handle a skill that doesn't follow the required SKILL.md schema?
- What happens when /Pending_Approval/ contains stale approval requests (older than 7 days)?
- How does the system handle log file rotation when /Logs/YYYY-MM-DD.json grows too large?

## Requirements

### Functional Requirements

#### Core Constitutional Principles

- **FR-001**: System MUST store all data locally (no cloud synchronization of operational data)
- **FR-002**: System MUST use .env file for all credentials and sensitive configuration
- **FR-003**: System MUST include .env in .gitignore to prevent credential leakage
- **FR-004**: System MUST block execution of high-risk actions until human approval is granted
- **FR-005**: System MUST log every action to /Logs/YYYY-MM-DD.json with complete metadata
- **FR-006**: System MUST continue task execution until task moves to /Done/ or emits `<promise>TASK_COMPLETE</promise>`
- **FR-007**: System MUST implement at least one proactive watcher that creates tasks in /Needs_Action/

#### Directory Structure

- **FR-008**: System MUST implement the following directory structure at project root:
  - /Business_Goals.md
  - /Dashboard.md
  - /Logs/
  - /Pending_Approval/
  - /Briefings/
  - /Done/
  - /Needs_Action/
  - .claude/skills/

- **FR-009**: System MUST create directories automatically if they don't exist on first run

#### Required Skills

- **FR-010**: System MUST implement Task Orchestrator skill at .claude/skills/task-orchestrator/SKILL.md
- **FR-011**: Task Orchestrator MUST create Plan.md for multi-step tasks
- **FR-012**: Task Orchestrator MUST track task status and move completed tasks to /Done/
- **FR-013**: Task Orchestrator MUST log all state transitions

- **FR-014**: System MUST implement Approval Guard skill at .claude/skills/approval-guard/SKILL.md
- **FR-015**: Approval Guard MUST evaluate action risk level (Low/Medium/High)
- **FR-016**: Approval Guard MUST compare risk against constitutional thresholds
- **FR-017**: Approval Guard MUST create /Pending_Approval/[task-id].md for high-risk actions
- **FR-018**: Approval Guard MUST block execution until approval file is manually approved

- **FR-019**: System MUST implement Logging & Audit skill at .claude/skills/logging-audit/SKILL.md
- **FR-020**: Logging skill MUST record timestamp, action, skill used, risk classification, and approval status for every action
- **FR-021**: Logging skill MUST flag constitutional violations in logs
- **FR-022**: Logging skill MUST create new log file per day (YYYY-MM-DD.json format)

#### SKILL.md Schema Compliance

- **FR-023**: Every skill MUST have a SKILL.md file following the required schema
- **FR-024**: SKILL.md MUST include sections: Purpose, Constitutional Alignment, Inputs, Outputs, Risk Classification, Execution Logic, HITL Checkpoint, Logging Requirements, Failure Handling, Completion Condition
- **FR-025**: Risk Classification MUST be one of: Low, Medium, High

#### Workflow Demonstration

- **FR-026**: System MUST demonstrate at least one complete autonomous workflow from trigger to completion
- **FR-027**: Workflow MUST include: event detection → task creation → risk evaluation → execution/approval → logging → completion

#### Autonomy Level Constraints (Bronze = Level 1)

- **FR-028**: System MUST NOT execute financial transactions autonomously
- **FR-029**: System MUST NOT delete files without approval
- **FR-030**: System MUST NOT send external emails without approval (drafting is allowed)
- **FR-031**: System MUST NOT post to social media autonomously (drafting is allowed)
- **FR-032**: System MUST NOT support multi-agent collaboration at Bronze tier

#### Security Requirements

- **FR-033**: System MUST provide .env.example file with all required configuration keys
- **FR-034**: System MUST support DRY_RUN mode for testing without executing actions
- **FR-035**: System MUST NOT store credentials in plain text outside of .env
- **FR-036**: System MUST remind user to rotate credentials monthly (via log or dashboard)

### Key Entities

- **Task**: Represents a unit of work to be executed. Attributes include task ID, description, priority, risk level, status (pending/in-progress/completed), created timestamp, completion timestamp, assigned skill.

- **Approval Request**: Represents a high-risk action awaiting human approval. Attributes include request ID, task reference, action description, risk justification, created timestamp, approval status (pending/approved/rejected), approver identity.

- **Log Entry**: Represents a single action taken by the system. Attributes include timestamp, action type, skill used, risk classification, approval status, outcome (success/failure), error details (if failed), constitutional compliance flag.

- **Skill Definition**: Represents a capability of the FTE. Attributes include skill name, purpose, constitutional alignment, input triggers, output artifacts, risk classification, execution steps, HITL checkpoints, logging requirements.

- **Watcher**: Represents a proactive monitoring system. Attributes include watcher type (email/file/schedule), trigger conditions, polling interval, task template, enabled status.

## Success Criteria

### Measurable Outcomes

- **SC-001**: System successfully executes at least one complete workflow (trigger → task → approval → execution → logging → completion) within 5 minutes of trigger event
- **SC-002**: All high-risk actions create approval files in /Pending_Approval/ and block execution until manually approved
- **SC-003**: 100% of actions are logged in /Logs/YYYY-MM-DD.json with complete metadata (no missing fields)
- **SC-004**: System continues task execution through at least one retry after transient failure before requesting human help
- **SC-005**: All three required skills (Task Orchestrator, Approval Guard, Logging & Audit) are present and follow the required SKILL.md schema
- **SC-006**: System operates entirely from local storage with no cloud dependencies for core functionality
- **SC-007**: No credentials or secrets are committed to version control (.env is in .gitignore)
- **SC-008**: System can be audited by reviewing log files alone - all actions are traceable
- **SC-009**: At least one proactive watcher successfully detects events and creates tasks in /Needs_Action/ without manual intervention
- **SC-010**: System passes all constitutional compliance checks (Local-First, HITL, Transparency, Persistence, Proactivity, Cost Efficiency)

## Assumptions

- The system will run on a local development machine with file system access
- Users have basic understanding of file system navigation and manual approval workflows
- The initial workflow demonstration will use a simple trigger (e.g., file watcher or scheduled task) rather than complex integrations
- Approval files in /Pending_Approval/ will be manually edited by users to indicate approval (e.g., changing status field)
- Log files will use JSON format for structured querying and analysis
- The system will use a polling mechanism for watchers (not real-time event streams)
- DRY_RUN mode will simulate actions and log them without making actual changes
- Monthly credential rotation reminders will be passive (logged) rather than enforced

## Dependencies

- File system access (read/write permissions for project directory)
- .env file management capability
- JSON parsing and generation capability
- File watching or polling capability for proactive monitoring
- Date/time utilities for log file naming and timestamps

## Out of Scope

- Multi-agent collaboration (reserved for Silver/Gold tiers)
- Real-time event streaming (polling is sufficient for Bronze)
- Advanced workflow orchestration (complex dependencies, parallel execution)
- External API integrations beyond basic email/file operations
- Automated credential rotation (only reminders required)
- Web-based dashboard UI (file-based dashboard is sufficient)
- Rollback or undo capabilities for completed actions
- Advanced error recovery strategies (simple retry is sufficient)
- Performance optimization for high-volume task processing
- Distributed or cloud deployment

## Constraints

- Must operate entirely on local file system (no cloud storage)
- Must not require external services for core functionality
- Must be auditable through log files alone
- Must block high-risk actions until human approval
- Must follow exact directory structure specified
- Must implement exactly three required skills at Bronze tier
- Must not execute financial transactions or irreversible actions autonomously
- Must use standardized SKILL.md schema (no custom formats)

## Risks

1. **Risk**: Task loops indefinitely without reaching completion
   - **Mitigation**: Implement maximum retry count and timeout thresholds; create escalation task in /Needs_Action/ when limits exceeded

2. **Risk**: Log files grow unbounded and consume disk space
   - **Mitigation**: Implement log rotation policy (archive logs older than 30 days); document disk space monitoring in operational guidelines

3. **Risk**: Approval files in /Pending_Approval/ become stale and forgotten
   - **Mitigation**: Dashboard displays pending approval count; log warnings for approvals older than 7 days

4. **Risk**: Concurrent tasks conflict when modifying shared resources
   - **Mitigation**: Implement simple file locking mechanism; document that Bronze tier does not support parallel task execution

5. **Risk**: .env file is accidentally committed despite .gitignore
   - **Mitigation**: Include pre-commit hook check in documentation; provide .env.example as template

## Next Steps

After specification approval:
1. Run `/sp.clarify` if any requirements need further clarification
2. Run `/sp.plan` to create architectural design and implementation plan
3. Run `/sp.tasks` to generate actionable task list with test cases
4. Run `/sp.implement` to execute the implementation plan
