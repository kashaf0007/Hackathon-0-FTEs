# Tasks: Silver Tier - Functional Business Assistant

**Input**: Design documents from `/specs/001-silver-tier-upgrade/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are omitted. Focus is on implementation and manual validation per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- **AI_Employee_Vault/**: All state, logs, and human-interaction files
- **.claude/skills/**: All AI reasoning logic
- **mcp_servers/**: MCP server implementations
- **scripts/**: Orchestration and scheduling
- **tests/**: Test files (for manual validation)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create AI_Employee_Vault directory structure (Logs/, Pending_Approval/, Approved/, Rejected/, Briefings/, Done/, Needs_Action/, Watchers/)
- [x] T002 Create .claude/skills directory structure (task-orchestrator/, approval-guard/, logging-audit/, linkedin-post-generator/, email-mcp-sender/, reasoning-loop/)
- [x] T003 Create mcp_servers/ and scripts/ directories
- [x] T004 Create tests/ directory structure (unit/, integration/, fixtures/)
- [x] T005 Create .env.example with all required environment variables per quickstart.md
- [x] T006 Create .gitignore with secrets exclusions (.env, *_token.json, *_credentials.json, .wwebjs_auth/)
- [x] T007 Create requirements.txt with Python dependencies (google-auth, google-api-python-client, selenium, jsonschema, schedule)
- [x] T008 [P] Create Business_Goals.md template in AI_Employee_Vault/
- [x] T009 [P] Create Dashboard.md template in AI_Employee_Vault/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Implement EventQueue class with atomic file operations in scripts/event_queue.py
- [x] T011 [P] Implement Logger class with JSON log format in scripts/logger.py
- [x] T012 [P] Implement file locking utilities (fcntl for Unix, msvcrt for Windows) in scripts/file_utils.py
- [x] T013 [P] Create event schema validator using jsonschema in scripts/event_validator.py
- [x] T014 Implement RiskClassifier with keyword-based classification in scripts/risk_classifier.py
- [x] T015 [P] Create MCP base server class with JSON-RPC support in mcp_servers/mcp_base.py
- [x] T016 [P] Implement DRY_RUN mode support in mcp_servers/mcp_base.py
- [x] T017 Create sample event fixtures in tests/fixtures/sample_events.json
- [x] T018 Create sample approval fixtures in tests/fixtures/sample_approvals.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Business Opportunity Detection (Priority: P1) 🎯

**Goal**: Continuously monitor multiple external sources and automatically create actionable task files

**Independent Test**: Send test emails/messages to monitored accounts and verify task files are created in Needs_Action/ with proper structure and logging

### Implementation for User Story 1

- [x] T019 [P] [US1] Create WatcherBase class with polling logic in AI_Employee_Vault/Watchers/watcher_base.py
- [x] T020 [P] [US1] Implement Gmail watcher with OAuth2 authentication in AI_Employee_Vault/Watchers/gmail_watcher.py
- [x] T021 [P] [US1] Implement LinkedIn watcher with Selenium automation in AI_Employee_Vault/Watchers/linkedin_watcher.py
- [x] T022 [P] [US1] Create watcher configuration schema in AI_Employee_Vault/Watchers/watcher_config.json
- [x] T023 [US1] Implement duplicate event detection in AI_Employee_Vault/Watchers/watcher_base.py
- [x] T024 [US1] Add event normalization to standard JSON format in AI_Employee_Vault/Watchers/watcher_base.py
- [x] T025 [US1] Integrate EventQueue for task file creation in AI_Employee_Vault/Watchers/watcher_base.py
- [x] T026 [US1] Add logging for all watcher detections using Logger class
- [x] T027 [US1] Create run_watchers.py script to execute all watchers in scripts/run_watchers.py

**Checkpoint**: At this point, watchers should detect events and create task files independently

---

## Phase 4: User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P1)

**Goal**: Enforce mandatory human approval for irreversible actions via file-based workflow

**Independent Test**: Trigger an action requiring approval and verify the system waits for manual file movement before proceeding

### Implementation for User Story 5

- [X] T028 [P] [US5] Create ApprovalWorkflow class in scripts/approval_workflow.py
- [X] T029 [P] [US5] Implement approval request file generation (Markdown format) in scripts/approval_workflow.py
- [X] T030 [P] [US5] Implement approval status checker (polls for file movement) in scripts/approval_workflow.py
- [X] T031 [US5] Implement timeout handler (24-hour default) in scripts/approval_workflow.py
- [X] T032 [US5] Create approval-guard skill SKILL.md in .claude/skills/approval-guard/SKILL.md
- [X] T033 [US5] Create approval-guard skill prompt template in .claude/skills/approval-guard/prompt.txt
- [X] T034 [US5] Create approval-guard skill examples in .claude/skills/approval-guard/examples.md
- [X] T035 [US5] Add approval logging for all requests and decisions

**Checkpoint**: Approval workflow should create requests, wait for human decision, and proceed accordingly

---

## Phase 5: User Story 3 - Structured Reasoning and Task Execution (Priority: P1)

**Goal**: Analyze complex tasks, create step-by-step execution plans, and track progress until completion

**Independent Test**: Provide a multi-step task and verify Plan.md is created, steps are executed in order, and status is updated throughout

### Implementation for User Story 3

- [X] T036 [P] [US3] Create Plan.md template structure in AI_Employee_Vault/Plan.md
- [X] T037 [P] [US3] Implement PlanGenerator class in scripts/plan_generator.py
- [X] T038 [P] [US3] Implement TaskAnalyzer for event classification in scripts/task_analyzer.py
- [X] T039 [US3] Create reasoning-loop skill SKILL.md in .claude/skills/reasoning-loop/SKILL.md
- [X] T040 [US3] Create reasoning-loop skill prompt template in .claude/skills/reasoning-loop/prompt.txt
- [X] T041 [US3] Create reasoning-loop skill examples in .claude/skills/reasoning-loop/examples.md
- [X] T042 [US3] Implement step executor with status tracking in scripts/step_executor.py
- [X] T043 [US3] Implement Plan.md updater (after each step) in scripts/plan_generator.py
- [X] T044 [US3] Implement error handler with recovery options in scripts/step_executor.py
- [X] T045 [US3] Integrate with RiskClassifier for risk assessment
- [X] T046 [US3] Integrate with ApprovalWorkflow for medium/high risk tasks
- [X] T047 [US3] Implement task completion handler (move to Done/) in scripts/step_executor.py
- [X] T048 [US3] Add comprehensive logging for reasoning loop operations

**Checkpoint**: Reasoning loop should process events, generate plans, execute steps, and complete tasks

---

## Phase 6: User Story 4 - External Action Execution via MCP (Priority: P2)

**Goal**: Execute real-world actions through standardized MCP servers with full logging and dry-run support

**Independent Test**: Trigger an email send or LinkedIn post action and verify it goes through the MCP server with proper logging

### Implementation for User Story 4

- [X] T049 [P] [US4] Implement Email MCP server with send_email method in mcp_servers/email_server.py
- [X] T050 [P] [US4] Implement Email MCP server get_status method in mcp_servers/email_server.py
- [X] T051 [P] [US4] Implement Email MCP server validate_address method in mcp_servers/email_server.py
- [X] T052 [P] [US4] Implement LinkedIn MCP server with create_post method in mcp_servers/linkedin_server.py
- [X] T053 [P] [US4] Implement LinkedIn MCP server delete_post method in mcp_servers/linkedin_server.py
- [X] T054 [P] [US4] Implement LinkedIn MCP server get_post_stats method in mcp_servers/linkedin_server.py
- [X] T055 [P] [US4] Implement LinkedIn MCP server validate_content method in mcp_servers/linkedin_server.py
- [X] T056 [US4] Create MCP client library for skill integration in scripts/mcp_client.py
- [X] T057 [US4] Implement MCP error handling and retry logic in mcp_servers/mcp_base.py
- [X] T058 [US4] Create email-mcp-sender skill SKILL.md in .claude/skills/email-mcp-sender/SKILL.md
- [X] T059 [US4] Create email-mcp-sender skill prompt template in .claude/skills/email-mcp-sender/prompt.txt
- [X] T060 [US4] Create email-mcp-sender skill examples in .claude/skills/email-mcp-sender/examples.md
- [X] T061 [US4] Add MCP action logging with timestamp and outcome
- [X] T062 [US4] Create MCP server configuration file in mcp_servers/server_config.json

**Checkpoint**: MCP servers should execute actions (or simulate in DRY_RUN mode) with full logging

---

## Phase 7: User Story 2 - Autonomous LinkedIn Business Posting (Priority: P2)

**Goal**: Generate and publish LinkedIn posts aligned with business goals via approval workflow

**Independent Test**: Trigger LinkedIn post generation workflow, verify draft creation, approval flow, and successful posting (or dry-run simulation)

### Implementation for User Story 2

- [X] T063 [P] [US2] Create linkedin-post-generator skill SKILL.md in .claude/skills/linkedin-post-generator/SKILL.md
- [X] T064 [P] [US2] Create linkedin-post-generator skill prompt template in .claude/skills/linkedin-post-generator/prompt.txt
- [X] T065 [P] [US2] Create linkedin-post-generator skill examples in .claude/skills/linkedin-post-generator/examples.md
- [X] T066 [US2] Implement Business_Goals.md reader in scripts/business_goals_reader.py
- [X] T067 [US2] Implement post content generator (reads Business_Goals.md) in scripts/post_generator.py
- [X] T068 [US2] Implement post draft creator (saves to Pending_Approval/) in scripts/post_generator.py
- [X] T069 [US2] Integrate with ApprovalWorkflow for post approval
- [X] T070 [US2] Integrate with LinkedIn MCP server for posting
- [X] T071 [US2] Implement post completion handler (move to Done/) in scripts/post_generator.py
- [X] T072 [US2] Create linkedin_scheduler.py for weekly post generation in scripts/linkedin_scheduler.py
- [X] T073 [US2] Add comprehensive logging for LinkedIn posting workflow

**Checkpoint**: LinkedIn posts should be generated, approved, and published with full audit trail

---

## Phase 8: User Story 6 - Automated Scheduling and Self-Execution (Priority: P3)

**Goal**: Run automatically on defined schedules without manual triggering

**Independent Test**: Configure the scheduler, wait for scheduled execution times, and verify tasks run automatically with proper logging

### Implementation for User Story 6

- [X] T074 [P] [US6] Create orchestrator.py for main orchestration loop in scripts/orchestrator.py
- [X] T075 [P] [US6] Create watchdog.py for system health monitoring in scripts/watchdog.py
- [X] T076 [P] [US6] Create update_dashboard.py for daily dashboard updates in scripts/update_dashboard.py
- [X] T077 [US6] Create scheduler_setup.sh for Linux/macOS cron configuration in scripts/scheduler_setup.sh
- [X] T078 [US6] Create setup_windows_scheduler.ps1 for Windows Task Scheduler in scripts/setup_windows_scheduler.ps1
- [X] T079 [US6] Create setup_macos_scheduler.sh for macOS launchd in scripts/setup_macos_scheduler.sh
- [X] T080 [US6] Create crontab.txt with cron job definitions in scripts/crontab.txt
- [X] T081 [US6] Implement scheduler failure recovery in scripts/orchestrator.py
- [X] T082 [US6] Add scheduler execution logging
- [X] T083 [US6] Create scheduler validation script in scripts/validate_scheduler.py

**Checkpoint**: All components should run automatically on schedule with proper logging and failure recovery

---

## Phase 9: Skill Architecture & Integration

**Purpose**: Complete skill-based architecture and cross-component integration

- [ ] T084 [P] Create task-orchestrator skill SKILL.md in .claude/skills/task-orchestrator/SKILL.md
- [ ] T085 [P] Create task-orchestrator skill prompt template in .claude/skills/task-orchestrator/prompt.txt
- [ ] T086 [P] Create task-orchestrator skill examples in .claude/skills/task-orchestrator/examples.md
- [ ] T087 [P] Create logging-audit skill SKILL.md in .claude/skills/logging-audit/SKILL.md
- [ ] T088 [P] Create logging-audit skill prompt template in .claude/skills/logging-audit/prompt.txt
- [ ] T089 [P] Create logging-audit skill examples in .claude/skills/logging-audit/examples.md
- [ ] T090 Integrate all skills with orchestrator.py
- [ ] T091 Verify all AI logic resides in .claude/skills/ (no AI in watcher scripts)
- [ ] T092 Verify all external actions go through MCP abstraction

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T093 [P] Create README.md with project overview and setup instructions
- [ ] T094 [P] Create CONTRIBUTING.md with development guidelines
- [ ] T095 [P] Implement log rotation for files older than 90 days in scripts/archive_logs.py
- [ ] T096 [P] Create health check script in scripts/health_check.py
- [ ] T097 [P] Create weekly report generator in scripts/generate_weekly_report.py
- [ ] T098 Validate all constitutional principles are enforced (Local-First, HITL, Transparency, Proactivity, Persistence, Cost Efficiency)
- [ ] T099 Run quickstart.md validation procedures (all 7 test procedures)
- [ ] T100 Verify Bronze tier functionality remains operational
- [ ] T101 Create troubleshooting documentation for common issues
- [ ] T102 Security audit: verify no credentials in code, all secrets in .env
- [ ] T103 Performance validation: verify watchers poll within 5-15 minutes, event processing < 30 seconds

---


## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Can start after Phase 2
- **User Story 5 (Phase 4)**: Depends on Foundational - Can start after Phase 2 (parallel with US1)
- **User Story 3 (Phase 5)**: Depends on Foundational, US1 (needs events), US5 (needs approval) - Start after US1 and US5
- **User Story 4 (Phase 6)**: Depends on Foundational - Can start after Phase 2 (parallel with US1/US5)
- **User Story 2 (Phase 7)**: Depends on US4 (MCP servers) and US5 (approval) - Start after US4 and US5
- **User Story 6 (Phase 8)**: Depends on all other user stories - Start after US1-US5 complete
- **Skill Architecture (Phase 9)**: Can be done in parallel with user stories
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational only - No dependencies on other stories
- **User Story 5 (P1)**: Depends on Foundational only - No dependencies on other stories
- **User Story 3 (P1)**: Depends on US1 (needs events to process) and US5 (needs approval workflow)
- **User Story 4 (P2)**: Depends on Foundational only - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US4 (MCP servers) and US5 (approval workflow)
- **User Story 6 (P3)**: Depends on all other stories (schedules their execution)

### Within Each User Story

- Models/classes before services
- Services before integration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**After Foundational Phase Completes**:
- US1 (Watchers), US5 (Approval), and US4 (MCP) can all start in parallel
- Within US1: T020 (Gmail watcher) and T021 (LinkedIn watcher) can run in parallel
- Within US4: T049-T055 (all MCP server methods) can run in parallel
- Within US5: T028-T030 (approval workflow components) can run in parallel

**After US1 and US5 Complete**:
- US3 (Reasoning Loop) can start

**After US4 and US5 Complete**:
- US2 (LinkedIn Posting) can start

**After All User Stories Complete**:
- US6 (Scheduling) can start
- Phase 9 (Skill Architecture) tasks can run in parallel
- Phase 10 (Polish) tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational components together:
Task: "Implement EventQueue class in scripts/event_queue.py"
Task: "Implement Logger class in scripts/logger.py"
Task: "Implement file locking utilities in scripts/file_utils.py"
Task: "Create event schema validator in scripts/event_validator.py"
Task: "Create MCP base server class in mcp_servers/mcp_base.py"
Task: "Implement DRY_RUN mode support in mcp_servers/mcp_base.py"
```

## Parallel Example: After Foundational Complete

```bash
# Launch US1, US5, and US4 together (different components, no dependencies):
Task: "Create WatcherBase class in AI_Employee_Vault/Watchers/watcher_base.py" (US1)
Task: "Create ApprovalWorkflow class in scripts/approval_workflow.py" (US5)
Task: "Implement Email MCP server in mcp_servers/email_server.py" (US4)
```

---

## Implementation Strategy

### MVP First (User Stories 1, 5, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Watchers)
4. Complete Phase 4: User Story 5 (Approval)
5. Complete Phase 5: User Story 3 (Reasoning Loop)
6. **STOP and VALIDATE**: Test US1+US5+US3 together - events detected, plans generated, approvals enforced
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Watchers) → Test independently → Events detected ✓
3. Add US5 (Approval) → Test independently → Approvals enforced ✓
4. Add US3 (Reasoning) → Test with US1+US5 → Plans generated and executed ✓ (MVP!)
5. Add US4 (MCP) → Test independently → External actions work ✓
6. Add US2 (LinkedIn) → Test with US4+US5 → Posts generated and published ✓
7. Add US6 (Scheduling) → Test with all → Fully autonomous ✓
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Watchers)
   - Developer B: User Story 5 (Approval)
   - Developer C: User Story 4 (MCP)
3. After US1+US5 complete:
   - Developer A: User Story 3 (Reasoning)
4. After US4+US5 complete:
   - Developer B: User Story 2 (LinkedIn)
5. After all complete:
   - Developer C: User Story 6 (Scheduling)

---

## Task Summary

**Total Tasks**: 103
**Tasks by Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 9 tasks
- Phase 3 (US1 - Watchers): 9 tasks
- Phase 4 (US5 - Approval): 8 tasks
- Phase 5 (US3 - Reasoning): 13 tasks
- Phase 6 (US4 - MCP): 14 tasks
- Phase 7 (US2 - LinkedIn): 11 tasks
- Phase 8 (US6 - Scheduling): 10 tasks
- Phase 9 (Skill Architecture): 9 tasks
- Phase 10 (Polish): 11 tasks

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Send test emails → verify task files created
- US5: Trigger approval → verify system waits for file movement
- US3: Provide multi-step task → verify Plan.md created and executed
- US4: Trigger MCP action → verify execution through MCP server
- US2: Trigger LinkedIn workflow → verify draft, approval, posting
- US6: Configure scheduler → verify automatic execution

**Suggested MVP Scope**: Phases 1-5 (Setup + Foundational + US1 + US5 + US3) = 48 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are absolute and match plan.md structure
- DRY_RUN mode must be respected throughout for safe testing
- All secrets must remain in .env, never in code
