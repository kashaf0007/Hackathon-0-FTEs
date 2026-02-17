# Implementation Plan: Silver Tier - Functional Business Assistant

**Branch**: `001-silver-tier-upgrade` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-silver-tier-upgrade/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Silver Tier transforms the Digital FTE from a reactive automation system (Bronze) into a proactive, reasoning-capable business assistant. The system will monitor multiple external sources (Gmail, WhatsApp, LinkedIn), generate structured execution plans, execute real-world actions through MCP servers, enforce human-in-the-loop approval for sensitive operations, and run autonomously on scheduled intervals. All AI reasoning logic will be modularized into Claude skills, with watchers handling only event detection. The architecture enforces constitutional principles including Local-First storage, HITL safety, Transparency through logging, Proactivity in business operations, Persistence until task completion, and Cost Efficiency through automation.

## Technical Context

**Language/Version**: Python 3.11+ (for watchers, MCP servers, orchestration scripts)
**Primary Dependencies**:
- Gmail API client (google-auth, google-api-python-client)
- WhatsApp automation (selenium/playwright for web.whatsapp.com or whatsapp-web.js via Node bridge)
- LinkedIn API (linkedin-api or selenium for automation)
- MCP framework (to be researched - likely custom JSON-RPC implementation)
- Schedule library (schedule or APScheduler for Python-based scheduling)
- JSON schema validation (jsonschema)

**Storage**: File-based (JSON for events/logs/approvals, Markdown for plans/briefings/tasks)
**Testing**: pytest for Python components, integration tests for watcher-to-skill workflows
**Target Platform**: Cross-platform (Windows Task Scheduler, Linux cron, macOS launchd)
**Project Type**: Single project with modular skill architecture under .claude/skills/
**Performance Goals**:
- Watchers poll every 5-15 minutes without blocking
- Event processing latency < 30 seconds
- Plan generation < 2 minutes for complex tasks
- MCP action execution < 10 seconds

**Constraints**:
- All secrets in .env (never committed)
- All AI logic in .claude/skills/ (no AI in watcher scripts)
- All external actions through MCP abstraction (no direct API calls in skills)
- Bronze tier functionality must remain operational
- File-based state management (no database required)
- Approval workflow must be file-based (human moves files between directories)

**Scale/Scope**:
- 2-3 active watchers monitoring continuously
- 10-50 events per day
- 5-10 pending approvals per week
- 100-500 log entries per day
- 6 core skills (task-orchestrator, approval-guard, logging-audit, linkedin-post-generator, email-mcp-sender, reasoning-loop)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance Analysis

| Principle | Requirement | Design Compliance | Status |
|-----------|-------------|-------------------|--------|
| **Local-First** | All sensitive data stays on local machine, no cloud storage of secrets | Credentials in .env, WhatsApp sessions local, all state in AI_Employee_Vault/ | ✅ PASS |
| **HITL Safety** | Irreversible actions require explicit approval via file movement | Pending_Approval/ workflow for LinkedIn posts, emails, payments | ✅ PASS |
| **Proactivity** | System monitors and takes initiative without commands | Watchers poll continuously, LinkedIn posts generated weekly, reasoning loop auto-triggers | ✅ PASS |
| **Persistence** | Tasks continue until verifiably complete | Reasoning loop updates Plan.md until task in Done/, Ralph Wiggum hook integration | ✅ PASS |
| **Transparency** | Every action logged in /Logs/ | All watcher detections, MCP actions, approvals logged with timestamps | ✅ PASS |
| **Cost Efficiency** | Automate routine tasks at scale | Automated monitoring, posting, email handling reduces manual intervention | ✅ PASS |

### Rules of Engagement Compliance

| Rule | Design Implementation | Status |
|------|----------------------|--------|
| Never send emotional/legal/medical messages autonomously | Risk classifier skill flags these for approval | ✅ PASS |
| Flag payments > $500 or new payees | Approval guard checks payment metadata | ✅ PASS |
| Social media: draft only, never reply without approval | LinkedIn posts go to Pending_Approval/, no auto-replies | ✅ PASS |
| Check Business_Goals.md before business decisions | LinkedIn post generator reads Business_Goals.md | ✅ PASS |
| When in doubt → Pending_Approval/ | Risk classifier defaults to approval for medium/high risk | ✅ PASS |

### Autonomy Boundaries Compliance

| Action Category | Auto-Approve Threshold | Design Implementation | Status |
|-----------------|------------------------|----------------------|--------|
| Email replies | Known contacts, low risk | Email MCP sender checks contact history, risk level | ✅ PASS |
| Payments | < $50 recurring | Approval guard enforces thresholds | ✅ PASS |
| Social media | Scheduled posts (draft only) | All LinkedIn posts require approval | ✅ PASS |
| File operations | Create/read/move inside vault | Watchers only write to Needs_Action/, skills move to Done/ | ✅ PASS |

### Security & Privacy Compliance

| Requirement | Design Implementation | Status |
|-------------|----------------------|--------|
| Never store credentials in plain text | .env file with environment variables, .gitignore enforced | ✅ PASS |
| Every action logged | Logging-audit skill writes to Logs/YYYY-MM-DD.json | ✅ PASS |
| DRY_RUN mode respected | All MCP servers check DRY_RUN env var before execution | ✅ PASS |
| Secrets never synced to cloud | .gitignore includes .env, WhatsApp sessions, credentials | ✅ PASS |

### Gate Evaluation: ✅ ALL GATES PASSED

No constitutional violations detected. Design fully complies with all principles, rules, autonomy boundaries, and security requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-silver-tier-upgrade/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions and patterns
├── data-model.md        # Phase 1 output - entity schemas and state machines
├── quickstart.md        # Phase 1 output - setup and testing guide
├── contracts/           # Phase 1 output - MCP server contracts
│   ├── email-mcp.json       # Email sending MCP contract
│   ├── linkedin-mcp.json    # LinkedIn posting MCP contract
│   └── event-schema.json    # Standard event format schema
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Business_Goals.md        # Business objectives and messaging guidelines
├── Dashboard.md             # Current system status and activity summary
├── Plan.md                  # Active execution plan (generated by reasoning-loop skill)
├── Logs/                    # Action audit trail
│   └── YYYY-MM-DD.json      # Daily log files
├── Pending_Approval/        # Actions awaiting human approval
│   └── [action-id].md       # Approval request files
├── Approved/                # Human-approved actions ready for execution
├── Briefings/               # Weekly status reports
│   └── YYYY-MM-DD_Weekday_Briefing.md
├── Done/                    # Completed tasks archive
│   └── [task-id].md         # Completed task files
├── Needs_Action/            # Detected events requiring processing
│   └── [event-id].json      # Event files from watchers
└── Watchers/                # Event detection scripts
    ├── gmail_watcher.py     # Gmail monitoring
    ├── whatsapp_watcher.py  # WhatsApp monitoring
    ├── linkedin_watcher.py  # LinkedIn monitoring
    └── watcher_config.json  # Watcher configuration

.claude/
└── skills/                  # AI reasoning modules
    ├── task-orchestrator/
    │   ├── SKILL.md         # Skill definition and capabilities
    │   ├── examples.md      # Usage examples
    │   └── prompt.txt       # Skill prompt template
    ├── approval-guard/
    │   ├── SKILL.md
    │   ├── examples.md
    │   └── prompt.txt
    ├── logging-audit/
    │   ├── SKILL.md
    │   ├── examples.md
    │   └── prompt.txt
    ├── linkedin-post-generator/
    │   ├── SKILL.md
    │   ├── examples.md
    │   └── prompt.txt
    ├── email-mcp-sender/
    │   ├── SKILL.md
    │   ├── examples.md
    │   └── prompt.txt
    └── reasoning-loop/
        ├── SKILL.md
        ├── examples.md
        └── prompt.txt

mcp_servers/                 # MCP server implementations
├── email_server.py          # Email sending MCP server
├── linkedin_server.py       # LinkedIn posting MCP server
├── mcp_base.py              # Base MCP server class
└── server_config.json       # MCP server configuration

scripts/                     # Orchestration and scheduling
├── orchestrator.py          # Main orchestration loop
├── watchdog.py              # System health monitoring
├── scheduler_setup.sh       # Scheduler configuration script
└── run_watchers.py          # Watcher execution script

tests/
├── integration/
│   ├── test_watcher_to_skill.py      # End-to-end watcher → skill flow
│   ├── test_approval_workflow.py     # HITL approval flow
│   └── test_mcp_integration.py       # MCP server integration
├── unit/
│   ├── test_watchers.py              # Watcher logic tests
│   ├── test_event_parsing.py        # Event format validation
│   └── test_risk_classification.py   # Risk classifier tests
└── fixtures/
    ├── sample_events.json            # Test event data
    └── sample_approvals.md           # Test approval files

.env.example                 # Environment variable template
requirements.txt             # Python dependencies
README.md                    # Project setup and usage
```

**Structure Decision**: Single project structure with clear separation of concerns:
- **AI_Employee_Vault/**: All state, logs, and human-interaction files (file-based state management)
- **.claude/skills/**: All AI reasoning logic (enforces "no AI in scripts" rule)
- **mcp_servers/**: External action abstraction layer (enforces "no direct API calls" rule)
- **Watchers/**: Event detection only (no reasoning, just JSON generation)
- **scripts/**: Orchestration and scheduling (glue code, no business logic)

This structure enforces constitutional principles through directory boundaries and makes Bronze → Silver upgrade non-breaking (additive only).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional requirements satisfied by design.

## Phase 0: Research & Technology Decisions

**Status**: PENDING - See research.md (to be generated)

### Research Tasks

1. **MCP Framework Selection**
   - Research existing MCP (Model Context Protocol) implementations
   - Evaluate: custom JSON-RPC vs existing frameworks
   - Decision criteria: simplicity, logging support, DRY_RUN mode

2. **Gmail API Integration**
   - Research Gmail API authentication (OAuth2 flow)
   - Evaluate: official google-api-python-client vs alternatives
   - Decision criteria: ease of setup, rate limits, local credential storage

3. **WhatsApp Automation**
   - Research WhatsApp automation approaches
   - Evaluate: whatsapp-web.js (Node) vs selenium/playwright (Python)
   - Decision criteria: reliability, session persistence, detection risk

4. **LinkedIn API/Automation**
   - Research LinkedIn posting methods
   - Evaluate: official API vs selenium automation
   - Decision criteria: API access requirements, rate limits, reliability

5. **Scheduling Strategy**
   - Research cross-platform scheduling
   - Evaluate: OS-native (cron/Task Scheduler) vs Python APScheduler
   - Decision criteria: reliability, cross-platform support, failure recovery

6. **Event Bus Pattern**
   - Research file-based event queue patterns
   - Evaluate: JSON files vs SQLite vs message queue
   - Decision criteria: simplicity, no external dependencies, atomic operations

7. **Risk Classification**
   - Research risk assessment patterns for autonomous actions
   - Evaluate: rule-based vs ML-based classification
   - Decision criteria: accuracy, explainability, no external dependencies

8. **Approval Workflow Patterns**
   - Research file-based approval mechanisms
   - Evaluate: file movement vs status flags vs approval database
   - Decision criteria: human-friendly, atomic operations, audit trail

## Phase 1: Design & Contracts

**Status**: PENDING - See data-model.md, contracts/, quickstart.md (to be generated)

### Design Artifacts

1. **data-model.md**: Entity schemas and state machines
   - Event schema (standard format for all watchers)
   - Task schema (Needs_Action → Pending_Approval → Approved → Done)
   - Plan schema (Plan.md structure and state transitions)
   - Log schema (Logs/YYYY-MM-DD.json structure)
   - Approval schema (Pending_Approval/*.md structure)

2. **contracts/**: MCP server API contracts
   - email-mcp.json: Email sending contract (OpenAPI/JSON-RPC)
   - linkedin-mcp.json: LinkedIn posting contract
   - event-schema.json: Standard event format validation schema

3. **quickstart.md**: Setup and testing guide
   - Prerequisites and dependencies
   - Environment setup (.env configuration)
   - Watcher configuration
   - MCP server setup
   - Scheduler configuration
   - Testing procedures
   - Troubleshooting guide

## Phase 2: Task Breakdown

**Status**: NOT STARTED - Run `/sp.tasks` after Phase 1 completion

Task generation will create tasks.md with:
- Testable implementation tasks
- Dependency ordering
- Acceptance criteria for each task
- Test cases for validation

## Implementation Phases (Detailed Roadmap)

### Phase 1: Multi-Channel Watchers (6-8 hours)

**Objective**: Implement 2+ watchers that detect events and create standardized task files

**Components**:
1. Watcher base class with common polling logic
2. Gmail watcher (email detection)
3. WhatsApp watcher (message detection)
4. LinkedIn watcher (connection requests, messages)
5. Event normalization to standard JSON format
6. Event queue management (Needs_Action/ directory)

**Deliverables**:
- AI_Employee_Vault/Watchers/gmail_watcher.py
- AI_Employee_Vault/Watchers/whatsapp_watcher.py
- AI_Employee_Vault/Watchers/linkedin_watcher.py
- AI_Employee_Vault/Watchers/watcher_config.json
- tests/unit/test_watchers.py
- tests/integration/test_watcher_to_skill.py

**Acceptance Criteria**:
- Each watcher polls its source every 5-15 minutes
- New events create JSON files in Needs_Action/
- Events follow standard schema (source, type, timestamp, content, metadata)
- Duplicate detection prevents redundant task creation
- All detections logged to Logs/

### Phase 2: LinkedIn Auto-Posting System (3-4 hours)

**Objective**: Generate and post LinkedIn content with approval workflow

**Components**:
1. LinkedIn post generator skill (.claude/skills/linkedin-post-generator/)
2. Business_Goals.md reader
3. Post draft creation (Pending_Approval/)
4. LinkedIn MCP server (mcp_servers/linkedin_server.py)
5. Approval workflow integration

**Deliverables**:
- .claude/skills/linkedin-post-generator/SKILL.md
- .claude/skills/linkedin-post-generator/prompt.txt
- mcp_servers/linkedin_server.py
- AI_Employee_Vault/Business_Goals.md (template)
- tests/integration/test_linkedin_workflow.py

**Acceptance Criteria**:
- Post generator reads Business_Goals.md
- Generated posts align with business objectives
- Drafts saved to Pending_Approval/
- System waits for human approval (file move to Approved/)
- Approved posts published via MCP server
- All steps logged

### Phase 3: Claude Reasoning Loop + Plan.md (4-5 hours)

**Objective**: Structured task analysis and execution planning

**Components**:
1. Reasoning loop skill (.claude/skills/reasoning-loop/)
2. Plan.md generator
3. Task analyzer
4. Risk classifier
5. Step executor with status tracking

**Deliverables**:
- .claude/skills/reasoning-loop/SKILL.md
- .claude/skills/reasoning-loop/prompt.txt
- AI_Employee_Vault/Plan.md (template)
- tests/unit/test_plan_generation.py
- tests/integration/test_reasoning_loop.py

**Acceptance Criteria**:
- Tasks in Needs_Action/ trigger plan generation
- Plan.md contains objective, context, actions, risk level
- Plan.md updated after each step execution
- Errors captured in Plan.md with recovery options
- Completed tasks moved to Done/

### Phase 4: MCP Server Integration (4-5 hours)

**Objective**: External action execution through MCP abstraction

**Components**:
1. MCP base server class (mcp_servers/mcp_base.py)
2. Email MCP server (mcp_servers/email_server.py)
3. LinkedIn MCP server (mcp_servers/linkedin_server.py)
4. Email sender skill (.claude/skills/email-mcp-sender/)
5. MCP client library
6. DRY_RUN mode support

**Deliverables**:
- mcp_servers/mcp_base.py
- mcp_servers/email_server.py
- mcp_servers/linkedin_server.py
- .claude/skills/email-mcp-sender/SKILL.md
- contracts/email-mcp.json
- contracts/linkedin-mcp.json
- tests/integration/test_mcp_integration.py

**Acceptance Criteria**:
- At least one MCP server functional (email or LinkedIn)
- All external actions routed through MCP
- DRY_RUN mode simulates actions without execution
- All MCP calls logged with timestamp and outcome
- MCP failures logged and flagged for human review

### Phase 5: Human-in-the-Loop Approval (3-4 hours)

**Objective**: Enforce approval workflow for sensitive actions

**Components**:
1. Approval guard skill (.claude/skills/approval-guard/)
2. Risk classifier
3. Approval file generator
4. Approval status checker
5. Timeout handler

**Deliverables**:
- .claude/skills/approval-guard/SKILL.md
- .claude/skills/approval-guard/prompt.txt
- AI_Employee_Vault/Pending_Approval/ (directory structure)
- AI_Employee_Vault/Approved/ (directory structure)
- tests/integration/test_approval_workflow.py

**Acceptance Criteria**:
- Sensitive actions create approval files in Pending_Approval/
- Approval files contain action description and risk assessment
- System waits for file movement to Approved/
- Approved actions execute and move to Done/
- Timeout cancels unapproved actions
- All approval decisions logged

### Phase 6: Scheduling (2-3 hours)

**Objective**: Automated execution on defined schedules

**Components**:
1. Scheduler setup script (scripts/scheduler_setup.sh)
2. Watcher runner (scripts/run_watchers.py)
3. Orchestrator (scripts/orchestrator.py)
4. Watchdog monitor (scripts/watchdog.py)
5. OS-specific scheduler configuration

**Deliverables**:
- scripts/scheduler_setup.sh
- scripts/run_watchers.py
- scripts/orchestrator.py
- scripts/watchdog.py
- Documentation for Windows/Linux/Mac setup

**Acceptance Criteria**:
- Watchers run every 5-15 minutes automatically
- Reasoning loop runs every 10 minutes
- LinkedIn post generation runs weekly
- Dashboard.md updated daily
- All scheduled executions logged
- Scheduler failures don't affect subsequent runs

### Phase 7: Skill-Based Architecture (integrated throughout)

**Objective**: All AI logic in .claude/skills/ with standardized structure

**Components**:
1. Task orchestrator skill (.claude/skills/task-orchestrator/)
2. Logging audit skill (.claude/skills/logging-audit/)
3. Skill template and documentation
4. Skill integration testing

**Deliverables**:
- .claude/skills/task-orchestrator/SKILL.md
- .claude/skills/logging-audit/SKILL.md
- All 6 required skills with SKILL.md, examples.md, prompt.txt
- Skill development guide

**Acceptance Criteria**:
- All AI reasoning in .claude/skills/
- No AI logic in watcher scripts
- Each skill has SKILL.md, examples.md, prompt.txt
- Skills are independently testable
- Skill integration tests pass

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| WhatsApp automation detection | High - account ban | Use official API if available, implement rate limiting, add human-like delays |
| LinkedIn API access restrictions | High - no posting capability | Fallback to selenium automation, implement retry logic |
| Gmail API rate limits | Medium - delayed processing | Implement exponential backoff, batch operations |
| File-based state race conditions | Medium - data corruption | Implement file locking, atomic operations |
| Scheduler reliability | Medium - missed executions | Implement watchdog monitoring, failure recovery |
| MCP server failures | Medium - action execution blocked | Implement retry logic, fallback mechanisms |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Approval workflow ignored | High - unauthorized actions | Enforce approval checks in code, log all bypasses |
| Log storage growth | Low - disk space | Implement log rotation, archival strategy |
| Credential exposure | High - security breach | .env in .gitignore, credential rotation reminders |
| Bronze tier regression | Medium - existing functionality broken | Comprehensive integration tests, feature flags |

## Success Metrics

### Functional Metrics
- 2+ watchers operational and detecting events
- LinkedIn posts generated weekly with 100% approval compliance
- Plan.md generated for all multi-step tasks
- 1+ MCP server functional with successful action execution
- 100% of sensitive actions go through approval workflow
- System runs continuously for 7 days with scheduled execution

### Quality Metrics
- All constitutional principles enforced (6/6)
- All actions logged with timestamp and outcome
- Zero credential exposures or security violations
- Bronze tier functionality remains 100% operational
- Test coverage > 80% for critical paths

### Performance Metrics
- Watcher polling interval: 5-15 minutes
- Event processing latency: < 30 seconds
- Plan generation time: < 2 minutes
- MCP action execution: < 10 seconds
- System uptime: > 99% over 7 days

## Next Steps

1. **Complete Phase 0 Research** (run research tasks, generate research.md)
2. **Complete Phase 1 Design** (generate data-model.md, contracts/, quickstart.md)
3. **Update Agent Context** (run update-agent-context script)
4. **Generate Tasks** (run `/sp.tasks` to create tasks.md)
5. **Begin Implementation** (run `/sp.implement` to execute tasks)

## Architectural Decision Records (ADRs)

Significant architectural decisions to be documented:

1. **File-Based State Management** - Why file system over database
2. **MCP Abstraction Layer** - Why MCP over direct API calls
3. **Skill-Based Architecture** - Why skills over monolithic scripts
4. **OS-Native Scheduling** - Why cron/Task Scheduler over Python scheduler
5. **Approval via File Movement** - Why file movement over status flags

Run `/sp.adr <decision-title>` to document each decision after planning phase.
