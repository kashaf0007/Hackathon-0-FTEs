# Feature Specification: Silver Tier - Functional Business Assistant

**Feature Branch**: `001-silver-tier-upgrade`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "Silver Tier upgrades Bronze from Controlled Automation to a Functional Business Assistant with multi-watcher monitoring, LinkedIn automation, reasoning loops, MCP integration, HITL workflows, and scheduling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Business Opportunity Detection (Priority: P1)

The Digital FTE continuously monitors multiple external sources (Gmail, WhatsApp, LinkedIn) for business-relevant events and automatically creates actionable tasks without human intervention.

**Why this priority**: This is the foundation of Silver Tier - transforming from reactive to proactive operation. Without multi-source monitoring, the system cannot operate autonomously.

**Independent Test**: Can be fully tested by sending test emails/messages to monitored accounts and verifying that task files are created in AI_Employee_Vault/Needs_Action/ with proper structure and logging.

**Acceptance Scenarios**:

1. **Given** the watcher system is running, **When** a new email arrives in Gmail matching business criteria, **Then** a structured task file is created in Needs_Action/ and the event is logged
2. **Given** multiple watchers are active, **When** events occur simultaneously across different sources, **Then** each event generates a separate task file without conflicts
3. **Given** a watcher detects an event, **When** the task file is created, **Then** it contains all required metadata (source, timestamp, priority, content summary)

---

### User Story 2 - Autonomous LinkedIn Business Posting (Priority: P2)

The Digital FTE generates and publishes LinkedIn posts aligned with business goals, following an approval workflow before posting to ensure quality and brand alignment.

**Why this priority**: Demonstrates proactive revenue-generating activity and external execution capability. This proves the system can create outbound business value, not just respond to inputs.

**Independent Test**: Can be fully tested by triggering the LinkedIn post generation workflow, verifying draft creation, approval flow, and successful posting (or dry-run simulation).

**Acceptance Scenarios**:

1. **Given** Business_Goals.md contains target audience and messaging guidelines, **When** the weekly posting schedule triggers, **Then** a LinkedIn post draft is generated and placed in Pending_Approval/
2. **Given** a post draft is in Pending_Approval/, **When** a human moves it to Approved/, **Then** the post is published to LinkedIn and moved to Done/
3. **Given** a post draft is rejected, **When** it remains in Pending_Approval/ beyond timeout period, **Then** the system logs the rejection and does not post
4. **Given** the posting workflow executes, **When** any step occurs, **Then** all actions are logged with timestamps and outcomes

---

### User Story 3 - Structured Reasoning and Task Execution (Priority: P1)

The Digital FTE analyzes complex tasks, creates step-by-step execution plans, tracks progress, and updates status until completion.

**Why this priority**: Core capability that enables autonomous operation. Without structured reasoning, the system cannot handle multi-step workflows reliably.

**Independent Test**: Can be fully tested by providing a multi-step task and verifying that Plan.md is created, steps are executed in order, and status is updated throughout.

**Acceptance Scenarios**:

1. **Given** a task file exists in Needs_Action/, **When** the reasoning loop processes it, **Then** a Plan.md is generated with step-by-step breakdown
2. **Given** a Plan.md exists, **When** the system executes steps, **Then** Plan.md is updated after each step with status and outcomes
3. **Given** a task encounters an error, **When** the reasoning loop detects the failure, **Then** the Plan.md is updated with error details and recovery options
4. **Given** all steps are complete, **When** the reasoning loop finishes, **Then** the task is moved to Done/ and final status is logged

---

### User Story 4 - External Action Execution via MCP (Priority: P2)

The Digital FTE executes real-world actions (sending emails, posting to LinkedIn, managing files) through standardized MCP servers with full logging and dry-run support.

**Why this priority**: Enables actual business impact beyond file manipulation. MCP abstraction ensures actions are auditable and reversible.

**Independent Test**: Can be fully tested by triggering an email send or LinkedIn post action and verifying it goes through the MCP server with proper logging.

**Acceptance Scenarios**:

1. **Given** an approved task requires sending an email, **When** the execution workflow runs, **Then** the email is sent via MCP server and logged
2. **Given** DRY_RUN mode is enabled, **When** any external action is triggered, **Then** the action is simulated and logged without actual execution
3. **Given** an MCP action fails, **When** the error occurs, **Then** the failure is logged with details and the task is marked for human review
4. **Given** any external action executes, **When** it completes, **Then** the action details are logged in Logs/ with timestamp and outcome

---

### User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P1)

The Digital FTE enforces mandatory human approval for irreversible actions (LinkedIn posting, email sending, payments) by creating approval files and waiting for human decision.

**Why this priority**: Critical safety mechanism. Without HITL enforcement, the system could execute harmful actions autonomously.

**Independent Test**: Can be fully tested by triggering an action requiring approval and verifying the system waits for manual file movement before proceeding.

**Acceptance Scenarios**:

1. **Given** a task requires LinkedIn posting, **When** the workflow reaches the posting step, **Then** a draft is created in Pending_Approval/ and execution pauses
2. **Given** a file is in Pending_Approval/, **When** a human moves it to Approved/, **Then** the workflow resumes and executes the action
3. **Given** multiple actions require approval, **When** they are triggered, **Then** each creates a separate approval file with clear action description
4. **Given** an approval file exists, **When** it is not approved within timeout period, **Then** the action is cancelled and logged

---

### User Story 6 - Automated Scheduling and Self-Execution (Priority: P3)

The Digital FTE runs automatically on defined schedules (watchers every 5-15 minutes, LinkedIn posts weekly, dashboard updates daily) without manual triggering.

**Why this priority**: Completes the autonomous operation model. Manual execution means the system is still reactive, not truly autonomous.

**Independent Test**: Can be fully tested by configuring the scheduler, waiting for scheduled execution times, and verifying tasks run automatically with proper logging.

**Acceptance Scenarios**:

1. **Given** the scheduler is configured, **When** the watcher schedule triggers, **Then** all watchers execute and log their activity
2. **Given** the weekly LinkedIn schedule triggers, **When** the time arrives, **Then** the post generation workflow executes automatically
3. **Given** the daily dashboard schedule triggers, **When** the time arrives, **Then** Dashboard.md is updated with current status
4. **Given** any scheduled task fails, **When** the failure occurs, **Then** the error is logged and the next scheduled run is not affected

---

### Edge Cases

- What happens when a watcher detects duplicate events (same email checked twice)?
- How does the system handle network failures during MCP action execution?
- What happens when Pending_Approval/ contains multiple files for the same action?
- How does the system recover if Plan.md becomes corrupted mid-execution?
- What happens when Business_Goals.md is missing or empty during LinkedIn post generation?
- How does the system handle timezone differences in scheduling?
- What happens when the Logs/ directory reaches storage limits?
- How does the system handle concurrent task execution conflicts?
- What happens when a watcher script crashes during execution?
- How does the system handle approval timeout edge cases (file moved exactly at timeout)?

## Requirements *(mandatory)*

### Functional Requirements

#### Multi-Watcher System

- **FR-001**: System MUST implement at least two functional watcher scripts that poll external sources
- **FR-002**: Watchers MUST detect new events from their respective sources (Gmail, WhatsApp, LinkedIn, or file system)
- **FR-003**: Watchers MUST create structured task files in AI_Employee_Vault/Needs_Action/ for each detected event
- **FR-004**: Watchers MUST log all detection events with timestamp, source, and event summary
- **FR-005**: Watchers MUST NOT execute actions directly - only generate task files
- **FR-006**: Watchers MUST run on a schedule of 5-15 minutes without manual triggering
- **FR-007**: Watchers MUST handle duplicate event detection to avoid creating redundant tasks

#### LinkedIn Automation

- **FR-008**: System MUST read Business_Goals.md to understand target audience and messaging guidelines
- **FR-009**: System MUST generate LinkedIn post drafts aligned with business goals
- **FR-010**: System MUST save post drafts to Pending_Approval/ before posting
- **FR-011**: System MUST wait for human approval (file moved to Approved/) before posting
- **FR-012**: System MUST post to LinkedIn only after approval is granted
- **FR-013**: System MUST log all posting activity including draft creation, approval, and publication
- **FR-014**: LinkedIn post generation MUST be implemented as a skill in .claude/skills/linkedin-post-generator/
- **FR-015**: System MUST execute LinkedIn posting on a weekly schedule

#### Reasoning Loop

- **FR-016**: System MUST automatically generate Plan.md for each task requiring multi-step execution
- **FR-017**: Plan.md MUST contain step-by-step reasoning, task breakdown, and status tracking
- **FR-018**: System MUST analyze tasks before creating execution plans
- **FR-019**: System MUST execute plan steps sequentially and update Plan.md after each step
- **FR-020**: System MUST continue execution until task is complete or encounters unrecoverable error
- **FR-021**: Reasoning loop MUST be implemented as a skill in .claude/skills/reasoning-loop/
- **FR-022**: System MUST handle errors gracefully and update Plan.md with error details and recovery options

#### MCP Integration

- **FR-023**: System MUST implement at least one working MCP server for external actions
- **FR-024**: System MUST route all external actions through MCP abstraction (no direct API calls)
- **FR-025**: System MUST log all MCP actions with timestamp, action type, and outcome
- **FR-026**: System MUST respect DRY_RUN mode for all external actions
- **FR-027**: MCP actions MUST be implemented as skills (e.g., .claude/skills/email-mcp-sender/)
- **FR-028**: System MUST handle MCP action failures and log error details

#### HITL Workflow

- **FR-029**: System MUST enforce approval flow for LinkedIn posting, email sending, payments, and irreversible actions
- **FR-030**: System MUST create approval files in Pending_Approval/ with clear action descriptions
- **FR-031**: System MUST wait for manual file movement to Approved/ before executing approved actions
- **FR-032**: System MUST integrate with Approval Guard Skill for all approval workflows
- **FR-033**: System MUST log all approval requests, decisions, and outcomes
- **FR-034**: System MUST handle approval timeouts and cancel actions that are not approved within timeout period

#### Scheduling

- **FR-035**: System MUST self-run via operating system scheduler (cron, Task Scheduler, or launchd)
- **FR-036**: System MUST execute watchers every 5-15 minutes automatically
- **FR-037**: System MUST execute LinkedIn post generation weekly automatically
- **FR-038**: System MUST update Dashboard.md daily automatically
- **FR-039**: System MUST log all scheduled executions with timestamp and outcome
- **FR-040**: System MUST handle scheduler failures gracefully without affecting subsequent runs

#### Architecture

- **FR-041**: All AI reasoning and decision-making logic MUST reside in .claude/skills/
- **FR-042**: Watcher scripts MUST contain only detection logic, no AI reasoning
- **FR-043**: System MUST maintain Bronze tier structure and add Silver tier components
- **FR-044**: System MUST implement required skills: task-orchestrator, approval-guard, logging-audit, linkedin-post-generator, email-mcp-sender, reasoning-loop
- **FR-045**: System MUST maintain directory structure: Business_Goals.md, Dashboard.md, Plan.md, Logs/, Pending_Approval/, Briefings/, Done/, Needs_Action/, Watchers/

#### Constitutional Enforcement

- **FR-046**: System MUST enforce Local-First principle (no cloud storage of secrets)
- **FR-047**: System MUST enforce HITL principle (approval files mandatory for irreversible actions)
- **FR-048**: System MUST enforce Transparency principle (every action logged)
- **FR-049**: System MUST enforce Proactivity principle (LinkedIn auto-sales generation)
- **FR-050**: System MUST enforce Persistence principle (reasoning loop until task completion)
- **FR-051**: System MUST enforce Cost Efficiency principle (automated outreach without manual intervention)

### Key Entities

- **Task File**: Represents a detected event or work item requiring action. Contains source, timestamp, priority, content summary, and status. Lives in Needs_Action/, Pending_Approval/, Approved/, or Done/.

- **Plan**: Represents a multi-step execution strategy for a complex task. Contains step breakdown, current status, completed steps, pending steps, and error history. Stored as Plan.md.

- **Watcher**: Represents an external source monitoring component. Contains polling schedule, source configuration, detection logic, and last-checked timestamp. Lives in Watchers/ directory.

- **Skill**: Represents an AI-driven capability module. Contains reasoning logic, execution workflow, and integration points. Lives in .claude/skills/ directory.

- **Approval Request**: Represents a pending human decision for an irreversible action. Contains action description, risk assessment, and approval status. Lives in Pending_Approval/ until approved or rejected.

- **Log Entry**: Represents a recorded system event. Contains timestamp, event type, actor, action, outcome, and error details. Lives in Logs/ directory.

- **Business Goal**: Represents strategic objectives and messaging guidelines. Contains target audience, key messages, success metrics, and brand voice. Stored in Business_Goals.md.

- **Dashboard**: Represents current system status and activity summary. Contains active tasks, recent completions, pending approvals, and system health. Stored as Dashboard.md.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully detects and creates task files for at least 2 different external sources (Gmail, WhatsApp, LinkedIn, or file system)
- **SC-002**: Watchers execute automatically every 5-15 minutes without manual triggering for 7 consecutive days
- **SC-003**: LinkedIn posts are generated weekly and published only after human approval
- **SC-004**: 100% of irreversible actions (LinkedIn posting, email sending) go through approval workflow before execution
- **SC-005**: Plan.md is automatically generated for all multi-step tasks and updated throughout execution
- **SC-006**: At least one external action (email or LinkedIn post) is successfully executed via MCP server
- **SC-007**: All system actions are logged with timestamp and outcome in Logs/ directory
- **SC-008**: Dashboard.md is updated daily with current system status automatically
- **SC-009**: System operates continuously for 7 days with scheduled execution and no manual intervention required
- **SC-010**: All AI reasoning logic resides in .claude/skills/ with no AI logic in watcher scripts
- **SC-011**: System enforces all 6 constitutional principles (Local-First, HITL, Transparency, Proactivity, Persistence, Cost Efficiency) with 100% compliance
- **SC-012**: Bronze tier functionality remains fully operational after Silver tier upgrade

### Assumptions

- Operating system scheduler (cron, Task Scheduler, or launchd) is available and configured
- External source credentials (Gmail, WhatsApp, LinkedIn) are available and valid
- Business_Goals.md exists and contains valid business objectives
- Bronze tier is fully functional before Silver tier upgrade begins
- MCP servers for required actions (email, LinkedIn) are available or can be implemented
- File system has sufficient storage for logs and task files
- Network connectivity is available for external source polling and MCP actions

### Out of Scope

- Multi-user support or role-based access control
- Advanced analytics or reporting dashboards
- Integration with external project management tools
- Mobile app or web interface
- Real-time notifications or alerts
- Advanced error recovery or self-healing capabilities
- Performance optimization for high-volume scenarios
- Multi-language support
- Advanced security features beyond basic authentication
- Cloud deployment or distributed architecture

### Dependencies

- Bronze tier must be fully functional and tested
- MCP server infrastructure must be available or implementable
- External source APIs (Gmail, WhatsApp, LinkedIn) must be accessible
- Operating system scheduler must be configurable
- .claude/skills/ directory structure must be established
- Constitutional principles must be documented and agreed upon

### Constraints

- All AI logic must reside in .claude/skills/ (no AI reasoning in scripts)
- Watchers must only detect events, not execute actions
- All irreversible actions must go through HITL approval workflow
- System must maintain Bronze tier structure and functionality
- Scheduling must use OS-native scheduler (no custom scheduling service)
- All actions must be logged for audit trail
- No cloud storage of secrets or sensitive data
- System must operate on local machine without external dependencies (except for external source APIs)
