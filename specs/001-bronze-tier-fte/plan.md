# Implementation Plan: Bronze Tier Constitutional FTE

**Branch**: `001-bronze-tier-fte` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-bronze-tier-fte/spec.md`

## Summary

Build a Minimum Viable Constitutional FTE (Bronze Tier) that implements structured autonomy with safety guardrails. The system will use AI_Employee_Vault/ as the operational workspace, implement three required skills (Task Orchestrator, Approval Guard, Logging & Audit), and demonstrate one complete autonomous workflow. The main.py file acts as the orchestrator entrypoint, continuously monitoring for tasks, evaluating risk, executing safe actions, and logging all operations while enforcing Human-in-the-Loop (HITL) approval boundaries for high-risk actions.

## Technical Context

**Language/Version**: Python 3.11+ (existing pyproject.toml detected)
**Primary Dependencies**:
- Standard library (json, pathlib, datetime, logging)
- python-dotenv (environment variable management)
- watchdog (file system monitoring for proactive watchers)
- pydantic (data validation for task/log schemas)

**Storage**: File-based (JSON for logs, Markdown for tasks/approvals/briefings)
**Testing**: pytest with coverage reporting
**Target Platform**: Local development machine (Windows/Linux/macOS)
**Project Type**: Single project - CLI orchestrator with file-based operations
**Performance Goals**:
- Task detection latency < 5 seconds
- Log write latency < 100ms
- Support 100+ tasks per day without degradation

**Constraints**:
- Must operate entirely offline (no cloud dependencies)
- Must not require external services for core functionality
- Must preserve all logs indefinitely (with rotation policy)
- Must block high-risk actions until manual approval

**Scale/Scope**:
- 3 required skills minimum
- 1 complete workflow demonstration
- Support 10-50 concurrent tasks in queue
- Daily log files (one per day)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **Local-First**: All data stored in AI_Employee_Vault/ and .claude/skills/. No cloud synchronization. Credentials in .env only.

✅ **Human-in-the-Loop (HITL) Safety**: Approval Guard skill enforces permission boundaries. High-risk actions create files in Pending_Approval/ and block execution.

✅ **Proactivity**: File watcher monitors Needs_Action/ directory. Orchestrator continuously polls for new tasks without manual intervention.

✅ **Ralph Wiggum Persistence**: Orchestrator loop continues until task moves to Done/ or emits `<promise>TASK_COMPLETE</promise>`. Retry logic for transient failures.

✅ **Transparency**: Logging & Audit skill records every action to Logs/YYYY-MM-DD.json with complete metadata (timestamp, action, skill, risk, approval status).

✅ **Cost Efficiency**: File-based operations minimize API costs. Local execution eliminates cloud service fees. Simple polling reduces complexity.

### Autonomy Level Compliance (Bronze = Level 1)

✅ **Permitted Actions**:
- Draft emails (no sending without approval)
- Create/read/move files within vault
- Log all operations
- Create approval requests

✅ **Blocked Actions** (require approval):
- Send external emails
- Delete files
- Execute payments
- Post to social media
- Any financial transaction

✅ **Not Supported** (out of scope for Bronze):
- Multi-agent collaboration
- External API integrations
- Real-time event streaming
- Advanced workflow orchestration

### Security & Privacy Compliance

✅ **.env Management**: .env.example provided, .env in .gitignore, credentials never in plain text
✅ **DRY_RUN Support**: Orchestrator respects DRY_RUN=true flag for testing
✅ **Audit Trail**: All actions logged with constitutional compliance flag
✅ **Credential Rotation**: Monthly reminder logged to Dashboard.md

### Gates Status

**Phase 0 Gate**: ✅ PASS - All constitutional principles addressed in design
**Phase 1 Gate**: ✅ PASS - Data model, contracts, and quickstart complete. All entities support constitutional requirements:
  - Task entity enforces state machine with approval checkpoints
  - Log Entry entity provides complete audit trail
  - Approval Request entity implements HITL safety
  - Skill Definition entity ensures structured capabilities
  - All schemas validated with JSON contracts

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-tier-fte/
├── spec.md              # Feature specification
├── plan.md              # This file (architectural design)
├── research.md          # Phase 0: Technology decisions and patterns
├── data-model.md        # Phase 1: Entity schemas and relationships
├── quickstart.md        # Phase 1: Setup and usage guide
├── contracts/           # Phase 1: Task/Log/Approval schemas
│   ├── task-schema.json
│   ├── log-schema.json
│   └── approval-schema.json
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
AI_Employee_Vault/          # Operational workspace (constitutional structure)
├── Business_Goals.md       # Business objectives and priorities
├── Dashboard.md            # Real-time status dashboard
├── Logs/                   # Daily action logs (YYYY-MM-DD.json)
├── Pending_Approval/       # High-risk actions awaiting approval
├── Briefings/              # Weekly summary reports
├── Done/                   # Completed tasks archive
└── Needs_Action/           # Task queue (proactive watcher creates here)

.claude/
└── skills/                 # Structured skill definitions
    ├── task-orchestrator/
    │   └── SKILL.md
    ├── approval-guard/
    │   └── SKILL.md
    └── logging-audit/
        └── SKILL.md

src/
├── orchestrator/           # Main orchestration logic
│   ├── __init__.py
│   ├── main.py            # Entry point - continuous task loop
│   ├── task_processor.py  # Task execution coordinator
│   └── config.py          # Configuration and .env loading
├── skills/                 # Skill implementations
│   ├── __init__.py
│   ├── base.py            # Base skill interface
│   ├── task_orchestrator.py
│   ├── approval_guard.py
│   └── logging_audit.py
├── models/                 # Data models (Pydantic schemas)
│   ├── __init__.py
│   ├── task.py
│   ├── log_entry.py
│   ├── approval_request.py
│   └── skill_definition.py
├── watchers/               # Proactive monitoring
│   ├── __init__.py
│   ├── base.py            # Base watcher interface
│   └── file_watcher.py    # File system watcher (demo workflow)
└── utils/                  # Shared utilities
    ├── __init__.py
    ├── file_ops.py        # Safe file operations
    └── validators.py      # Schema validation

tests/
├── unit/                   # Unit tests for individual components
│   ├── test_skills.py
│   ├── test_models.py
│   └── test_watchers.py
├── integration/            # Integration tests for workflows
│   ├── test_orchestrator.py
│   └── test_approval_flow.py
└── fixtures/               # Test data and mocks
    ├── sample_tasks/
    └── sample_logs/

.env.example                # Template for environment variables
.gitignore                  # Includes .env, AI_Employee_Vault/Logs/
pyproject.toml              # Python dependencies and project config
README.md                   # Project overview and setup instructions
```

**Structure Decision**: Single project structure selected because Bronze Tier is a standalone CLI orchestrator with no frontend/backend separation. All operations are file-based and local. The AI_Employee_Vault/ serves as the operational brain, while src/ contains the implementation logic. This structure supports the constitutional requirement for transparency (all operations visible in vault) and local-first operation (no external services).

## Complexity Tracking

No constitutional violations requiring justification. All design decisions align with Bronze Tier constraints and constitutional principles.

## Architecture Overview

### System Components

#### 1. Orchestrator (main.py)
**Responsibility**: Continuous task loop that monitors Needs_Action/, loads skills, processes tasks, and enforces persistence.

**Core Loop**:
```python
while True:
    tasks = scan_needs_action()
    for task in tasks:
        skill = load_skill(task.type)
        risk = approval_guard.evaluate(task)
        if risk == "HIGH":
            create_approval_request(task)
            continue
        result = skill.execute(task)
        logging_audit.log(task, result)
        if result.complete:
            move_to_done(task)
```

**Key Behaviors**:
- Polls Needs_Action/ every 5 seconds
- Loads skill definitions from .claude/skills/
- Enforces approval boundaries via Approval Guard
- Logs every action via Logging & Audit skill
- Moves completed tasks to Done/
- Retries failed tasks (max 3 attempts)
- Respects DRY_RUN flag

#### 2. Task Orchestrator Skill
**Responsibility**: Manage multi-step tasks, create Plan.md, track status, coordinate execution.

**Capabilities**:
- Parse task files (markdown format)
- Break complex tasks into steps
- Create Plan.md with step-by-step execution plan
- Track progress through state transitions
- Coordinate with other skills for execution
- Move completed tasks to Done/

**Risk Classification**: Low (orchestration only, no external actions)

#### 3. Approval Guard Skill
**Responsibility**: Evaluate action risk, enforce permission boundaries, create approval requests.

**Risk Evaluation Logic**:
```python
def evaluate_risk(action):
    if action.type in ["delete_file", "send_email", "payment"]:
        return "HIGH"
    if action.type in ["move_file_outside_vault", "bulk_operation"]:
        return "MEDIUM"
    return "LOW"
```

**Approval Request Format**:
```markdown
# Approval Request: [Task ID]

**Created**: [timestamp]
**Risk Level**: HIGH
**Action**: [description]

## Justification
[Why this action is needed]

## Impact
[What will happen if approved]

## Approval
Status: PENDING
Approver: [leave blank]
Decision: [APPROVE/REJECT]
Notes: [optional]
```

**Risk Classification**: Low (evaluation only, blocks execution)

#### 4. Logging & Audit Skill
**Responsibility**: Record all actions to daily log files, flag constitutional violations.

**Log Entry Schema**:
```json
{
  "timestamp": "2026-02-16T14:30:00Z",
  "task_id": "task-001",
  "action": "draft_email",
  "skill_used": "task-orchestrator",
  "risk_level": "LOW",
  "approval_status": "AUTO_APPROVED",
  "outcome": "SUCCESS",
  "error": null,
  "constitutional_compliance": true,
  "metadata": {
    "duration_ms": 150,
    "retry_count": 0
  }
}
```

**Logging Triggers**:
- Before task execution
- After task completion
- On task failure
- On approval request creation
- On approval decision
- On constitutional violation

**Risk Classification**: Low (logging only, no external actions)

#### 5. File Watcher (Demo Workflow)
**Responsibility**: Proactively monitor for trigger events, create tasks in Needs_Action/.

**Demo Workflow**: Email → Task → Draft Reply
1. Watcher detects new file in monitored directory (simulates email arrival)
2. Creates task file in Needs_Action/:
   ```markdown
   # Task: Draft Reply to [Subject]

   **Type**: draft_email
   **Priority**: MEDIUM
   **Created**: [timestamp]

   ## Context
   [Email content or trigger details]

   ## Expected Output
   Draft reply saved to this file
   ```
3. Orchestrator picks up task
4. Task Orchestrator creates Plan.md
5. Approval Guard evaluates (LOW risk for drafting)
6. Task executes (draft reply appended to task file)
7. Logging & Audit records action
8. Task moved to Done/

**Risk Classification**: Low (creates tasks only, no execution)

### Data Flow

```
[Trigger Event]
    ↓
[File Watcher] → Creates task file
    ↓
[Needs_Action/task-001.md]
    ↓
[Orchestrator] → Detects new task
    ↓
[Task Orchestrator] → Parses task, creates Plan.md
    ↓
[Approval Guard] → Evaluates risk
    ↓
    ├─ HIGH → [Pending_Approval/task-001.md] → STOP
    └─ LOW/MEDIUM → Continue
        ↓
    [Skill Execution] → Performs action
        ↓
    [Logging & Audit] → Records to Logs/YYYY-MM-DD.json
        ↓
    [Done/task-001.md] → Archive completed task
```

### State Transitions

**Task States**:
- PENDING: In Needs_Action/, not yet processed
- IN_PROGRESS: Being processed by orchestrator
- AWAITING_APPROVAL: In Pending_Approval/, blocked
- APPROVED: Approval granted, ready for execution
- COMPLETED: Successfully executed, in Done/
- FAILED: Execution failed after max retries

**Approval States**:
- PENDING: Awaiting human decision
- APPROVED: Human approved, ready for execution
- REJECTED: Human rejected, task cancelled

### Error Handling

**Transient Failures** (retry up to 3 times):
- File lock conflicts
- Temporary file system errors
- Parsing errors (malformed task files)

**Permanent Failures** (create help request):
- Invalid task schema
- Missing required fields
- Skill not found
- Constitutional violation detected

**Failure Response**:
1. Log error with full context
2. If retryable: increment retry count, wait 5s, retry
3. If max retries exceeded: create help request in Needs_Action/
4. If permanent: move to Done/ with FAILED status

### Security Considerations

**Credential Management**:
- All credentials in .env file
- .env in .gitignore (never committed)
- .env.example provided as template
- No credentials in logs or task files

**File System Security**:
- All operations within AI_Employee_Vault/ or .claude/
- No operations outside project directory without approval
- File deletion requires HIGH risk approval
- Atomic file operations (write to temp, then move)

**Audit Trail**:
- Every action logged with timestamp
- Log files immutable (append-only)
- Constitutional compliance flag on every entry
- Violations flagged for human review

**DRY_RUN Mode**:
- When DRY_RUN=true, simulate all actions
- Log simulated actions with DRY_RUN flag
- No actual file modifications
- Useful for testing and validation

## Key Design Decisions

### Decision 1: File-Based Task Queue
**Chosen**: Markdown files in Needs_Action/ directory
**Rationale**:
- Human-readable and editable
- No database dependency (local-first)
- Easy to inspect and debug
- Supports manual task creation
- Aligns with constitutional transparency

**Alternatives Considered**:
- SQLite database: Rejected (adds complexity, less transparent)
- JSON files: Rejected (less human-friendly)
- In-memory queue: Rejected (not persistent)

### Decision 2: Polling vs Event-Driven
**Chosen**: Polling (5-second interval)
**Rationale**:
- Simpler implementation for Bronze tier
- Sufficient for Bronze performance goals (<5s latency)
- No external dependencies (watchdog used only for demo watcher)
- Easier to debug and reason about

**Alternatives Considered**:
- Event-driven (inotify/FSEvents): Rejected (more complex, platform-specific)
- Real-time streaming: Rejected (out of scope for Bronze)

### Decision 3: Skill Definition Format
**Chosen**: Markdown files with required schema sections
**Rationale**:
- Human-readable documentation
- Self-documenting (purpose, inputs, outputs visible)
- Easy to validate schema compliance
- Supports non-technical stakeholders

**Alternatives Considered**:
- YAML: Rejected (less readable for long descriptions)
- JSON: Rejected (no comments, less human-friendly)
- Python classes: Rejected (not accessible to non-developers)

### Decision 4: Log Format
**Chosen**: Daily JSON files (YYYY-MM-DD.json)
**Rationale**:
- Structured data for programmatic analysis
- Daily rotation prevents unbounded growth
- JSON widely supported for querying/parsing
- Easy to archive old logs

**Alternatives Considered**:
- Plain text logs: Rejected (harder to parse)
- Single log file: Rejected (unbounded growth)
- Database: Rejected (adds complexity)

### Decision 5: Approval Mechanism
**Chosen**: Manual file editing (change status field)
**Rationale**:
- Simple for Bronze tier
- No UI required
- Transparent (file-based)
- Easy to audit

**Alternatives Considered**:
- CLI approval command: Rejected (more complex)
- Web UI: Rejected (out of scope for Bronze)
- Email approval: Rejected (requires external service)

## Phase 0: Research & Technology Validation

See [research.md](./research.md) for detailed technology decisions, best practices, and pattern validation.

**Key Research Areas**:
1. Python file watching patterns (watchdog library)
2. Pydantic schema validation best practices
3. JSON log rotation strategies
4. Markdown parsing and validation
5. Atomic file operations for concurrent access
6. DRY_RUN implementation patterns

## Phase 1: Data Model & Contracts

See [data-model.md](./data-model.md) for complete entity schemas and relationships.

**Key Entities**:
- Task (task-schema.json)
- Log Entry (log-schema.json)
- Approval Request (approval-schema.json)
- Skill Definition (skill-schema.json)
- Watcher Configuration (watcher-schema.json)

See [contracts/](./contracts/) for JSON schemas and validation rules.

## Phase 2: Implementation Tasks

Implementation tasks will be generated by `/sp.tasks` command after this plan is approved.

**Expected Task Categories**:
1. Setup & Infrastructure (directories, .env, dependencies)
2. Core Models (Pydantic schemas)
3. Skills Implementation (Task Orchestrator, Approval Guard, Logging & Audit)
4. Orchestrator (main loop, task processing)
5. Watchers (file watcher for demo workflow)
6. Testing (unit, integration, end-to-end)
7. Documentation (README, quickstart)

## Success Metrics

**Phase 0 Complete**: All research questions answered, technology choices validated
**Phase 1 Complete**: Data models defined, contracts created, quickstart written
**Phase 2 Complete**: All tasks in tasks.md completed, tests passing, demo workflow functional

**Bronze Tier Graduation Criteria**:
- ✅ AI_Employee_Vault/ fully structured
- ✅ 3 skills exist in .claude/skills/ with valid SKILL.md
- ✅ main.py acts as orchestrator with continuous loop
- ✅ Logs generated for all actions
- ✅ Approval system blocks high-risk actions
- ✅ One workflow fully automated (email → draft reply)
- ✅ DRY_RUN mode respected
- ✅ Persistence loop continues until task in Done/
- ✅ All constitutional principles enforced
- ✅ Tests passing (>80% coverage)

## Next Steps

1. Review and approve this plan
2. Run `/sp.tasks` to generate implementation task list
3. Run `/sp.implement` to execute tasks
4. Test Bronze Tier compliance with evaluation checklist
5. Document any architectural decisions as ADRs (if significant)

## Architectural Decision Records

No ADRs created yet. After implementation, consider documenting:
- File-based task queue vs database
- Polling vs event-driven architecture
- Markdown vs JSON for task files
