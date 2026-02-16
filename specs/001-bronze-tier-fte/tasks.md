# Tasks: Bronze Tier Constitutional FTE

**Input**: Design documents from `/specs/001-bronze-tier-fte/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not included as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths are relative to project root: `AI-Employee-Hackathon/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create AI_Employee_Vault directory structure (Business_Goals.md, Dashboard.md, Logs/, Pending_Approval/, Briefings/, Done/, Needs_Action/)
- [x] T002 Create .claude/skills directory structure (task-orchestrator/, approval-guard/, logging-audit/)
- [x] T003 Create src directory structure (orchestrator/, skills/, models/, watchers/, utils/)
- [x] T004 [P] Update pyproject.toml with dependencies (python-dotenv, watchdog, pydantic, pytest)
- [x] T005 [P] Create .env.example with required configuration keys (DRY_RUN, LOG_LEVEL, POLL_INTERVAL, MAX_RETRIES)
- [x] T006 [P] Update .gitignore to include .env and AI_Employee_Vault/Logs/
- [x] T007 [P] Create initial Business_Goals.md in AI_Employee_Vault/
- [x] T008 [P] Create initial Dashboard.md template in AI_Employee_Vault/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Create Task model with Pydantic schema in src/models/task.py
- [x] T010 [P] Create LogEntry model with Pydantic schema in src/models/log_entry.py
- [x] T011 [P] Create ApprovalRequest model with Pydantic schema in src/models/approval_request.py
- [x] T012 [P] Create SkillDefinition model with Pydantic schema in src/models/skill_definition.py
- [x] T013 [P] Create WatcherConfig model with Pydantic schema in src/models/watcher_config.py
- [x] T014 [P] Create models __init__.py to export all models in src/models/__init__.py
- [x] T015 [P] Create atomic file write utility in src/utils/file_ops.py
- [x] T016 [P] Create markdown parser utility in src/utils/file_ops.py
- [x] T017 [P] Create schema validator utility in src/utils/validators.py
- [x] T018 [P] Create utils __init__.py in src/utils/__init__.py
- [x] T019 Create Config class with .env loading in src/orchestrator/config.py
- [x] T020 Create base Skill interface in src/skills/base.py
- [x] T021 Create base Watcher interface in src/watchers/base.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 + 2 - Core Orchestration with Logging (Priority: P1) 🎯 MVP

**Goal**: Implement autonomous task execution with safety guardrails AND complete transparency through audit logging. These two stories are tightly coupled - the orchestrator requires logging to function properly.

**Independent Test**: Create a low-risk task in Needs_Action/, verify it executes automatically and logs the action. Create a high-risk task, verify it creates approval request and blocks execution. All actions should appear in Logs/YYYY-MM-DD.json.

### Implementation for User Story 1 + 2

- [x] T022 [P] [US1] [US2] Create Logging & Audit skill implementation in src/skills/logging_audit.py
- [x] T023 [P] [US1] Create Approval Guard skill implementation in src/skills/approval_guard.py
- [x] T024 [US1] Create Task Orchestrator skill implementation in src/skills/task_orchestrator.py (depends on T022, T023)
- [x] T025 [P] [US1] [US2] Create skills __init__.py to export all skills in src/skills/__init__.py
- [x] T026 [US1] Create TaskProcessor class for task execution coordination in src/orchestrator/task_processor.py
- [x] T027 [US1] Implement task scanning logic in TaskProcessor (scan Needs_Action/)
- [x] T028 [US1] Implement skill loading logic in TaskProcessor (load from .claude/skills/)
- [x] T029 [US1] Implement approval flow in TaskProcessor (check risk, create approval request if HIGH)
- [x] T030 [US1] Implement task execution logic in TaskProcessor (execute via skill)
- [x] T031 [US1] Implement task completion logic in TaskProcessor (move to Done/)
- [x] T032 [US2] Implement daily log file creation in Logging & Audit skill
- [x] T033 [US2] Implement log entry writing with atomic operations in Logging & Audit skill
- [x] T034 [US2] Implement constitutional compliance flagging in Logging & Audit skill
- [x] T035 [US1] Implement main orchestrator loop in src/orchestrator/main.py
- [x] T036 [US1] Add DRY_RUN mode support in main orchestrator loop
- [x] T037 [US1] Add graceful shutdown handling (KeyboardInterrupt) in main orchestrator
- [x] T038 [P] [US1] Create Task Orchestrator SKILL.md in .claude/skills/task-orchestrator/SKILL.md
- [x] T039 [P] [US1] Create Approval Guard SKILL.md in .claude/skills/approval-guard/SKILL.md
- [x] T040 [P] [US2] Create Logging & Audit SKILL.md in .claude/skills/logging-audit/SKILL.md

**Checkpoint**: At this point, the core orchestrator should be functional - tasks can be created, evaluated for risk, executed (if low risk) or blocked (if high risk), and all actions logged. This is the MVP.

---

## Phase 4: User Story 3 - Proactive Task Detection (Priority: P2)

**Goal**: Implement proactive monitoring that automatically creates tasks without manual intervention

**Independent Test**: Set up file watcher, create a file in monitored directory, verify task file is automatically created in Needs_Action/

### Implementation for User Story 3

- [x] T041 [P] [US3] Create FileWatcher class implementing base watcher interface in src/watchers/file_watcher.py
- [x] T042 [US3] Implement file system event detection using watchdog library in FileWatcher
- [x] T043 [US3] Implement task file creation logic in FileWatcher (create in Needs_Action/)
- [x] T044 [US3] Implement event filtering and debouncing in FileWatcher
- [x] T045 [US3] Add watcher configuration support in FileWatcher
- [x] T046 [P] [US3] Create watchers __init__.py in src/watchers/__init__.py
- [x] T047 [US3] Integrate FileWatcher into main orchestrator (start watcher thread)
- [x] T048 [US3] Add watcher graceful shutdown in main orchestrator

**Checkpoint**: At this point, the system can proactively detect events and create tasks automatically. Combined with US1+US2, this enables fully autonomous operation.

---

## Phase 5: User Story 4 - Persistent Task Execution (Priority: P2)

**Goal**: Implement retry logic and persistence to ensure tasks complete rather than being abandoned

**Independent Test**: Create a task that fails on first attempt, verify system retries up to 3 times before creating help request

### Implementation for User Story 4

- [x] T049 [US4] Add retry counter tracking in Task model (already in model, ensure used)
- [x] T050 [US4] Implement retry logic in TaskProcessor (increment retry_count, wait, retry)
- [x] T051 [US4] Implement max retry threshold check in TaskProcessor (max 3 retries)
- [x] T052 [US4] Implement help request creation for failed tasks in TaskProcessor
- [x] T053 [US4] Add transient vs permanent failure detection in TaskProcessor
- [x] T054 [US4] Implement task state persistence across orchestrator restarts
- [x] T055 [US4] Add incomplete task detection on orchestrator startup
- [x] T056 [US4] Implement task timeout detection and handling

**Checkpoint**: At this point, the system demonstrates Ralph Wiggum persistence - tasks are not abandoned and continue until completion or explicit failure.

---

## Phase 6: User Story 5 - Structured Skill Management (Priority: P3)

**Goal**: Implement skill loading, validation, and management system

**Independent Test**: Create a new skill with valid SKILL.md, verify it loads correctly. Create invalid SKILL.md, verify validation error.

### Implementation for User Story 5

- [x] T057 [P] [US5] Create SkillLoader class in src/skills/skill_loader.py
- [x] T058 [US5] Implement SKILL.md parsing logic in SkillLoader
- [x] T059 [US5] Implement required section validation in SkillLoader
- [x] T060 [US5] Implement skill schema validation against SkillDefinition model
- [x] T061 [US5] Add skill caching to avoid re-parsing in SkillLoader
- [x] T062 [US5] Implement skill discovery (scan .claude/skills/) in SkillLoader
- [x] T063 [US5] Add clear error messages for invalid skills in SkillLoader
- [x] T064 [US5] Integrate SkillLoader into TaskProcessor (replace manual loading)
- [x] T065 [US5] Add skill validation on orchestrator startup

**Checkpoint**: At this point, skills are properly managed with validation and clear error messages. New skills can be added by creating SKILL.md files.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final touches

- [x] T066 [P] Create comprehensive README.md with project overview and setup instructions
- [x] T067 [P] Add inline documentation and docstrings to all modules
- [x] T068 [P] Implement Dashboard.md auto-update logic (active tasks, pending approvals, completed today)
- [x] T069 [P] Add stale approval detection (warn for approvals >7 days old)
- [x] T070 [P] Implement monthly credential rotation reminder in Dashboard
- [x] T071 [P] Add log file size monitoring and rotation warnings
- [x] T072 Validate all SKILL.md files follow required schema
- [x] T073 Run end-to-end workflow test (file watcher → task → approval → execution → logging → completion)
- [x] T074 Verify all constitutional principles are enforced (Local-First, HITL, Proactivity, Persistence, Transparency, Cost Efficiency)
- [x] T075 Run Bronze Tier graduation checklist from quickstart.md
- [x] T076 [P] Code cleanup and remove any debug/temporary code
- [x] T077 [P] Verify .env is in .gitignore and not committed
- [x] T078 Final validation: Create sample tasks for all risk levels and verify correct handling

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories 1+2 (Phase 3)**: Depends on Foundational phase completion - Core MVP
- **User Story 3 (Phase 4)**: Depends on Foundational phase completion - Can run in parallel with US4, US5
- **User Story 4 (Phase 5)**: Depends on US1+US2 completion (needs TaskProcessor) - Can run in parallel with US3, US5
- **User Story 5 (Phase 6)**: Depends on Foundational phase completion - Can run in parallel with US3, US4
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1+2 (P1)**: Tightly coupled - orchestrator requires logging. Must be implemented together as MVP.
- **User Story 3 (P2)**: Independent - can start after Foundational. Integrates with US1 but doesn't modify it.
- **User Story 4 (P2)**: Depends on US1 TaskProcessor - extends retry logic. Can run after US1+US2.
- **User Story 5 (P3)**: Independent - can start after Foundational. Enhances US1 but doesn't break it.

### Within Each User Story

- Models and utilities before implementations
- Base classes before concrete implementations
- Skills before orchestrator integration
- Core logic before edge cases
- Implementation before SKILL.md documentation

### Parallel Opportunities

**Phase 1 (Setup)**: T004, T005, T006, T007, T008 can all run in parallel

**Phase 2 (Foundational)**: T009-T018 (all models and utilities) can run in parallel, then T019-T021 (config and base classes)

**Phase 3 (US1+US2)**: T022, T023, T038, T039, T040 can run in parallel (skills and docs in different files)

**Phase 4 (US3)**: T041, T046 can run in parallel

**Phase 7 (Polish)**: T066, T067, T068, T069, T070, T071, T076, T077 can all run in parallel

**Cross-Phase Parallelism**: After Foundational phase completes, US3, US5 can start in parallel. US4 can start after US1+US2 completes.

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all model creation tasks together:
Task: "Create Task model with Pydantic schema in src/models/task.py"
Task: "Create LogEntry model with Pydantic schema in src/models/log_entry.py"
Task: "Create ApprovalRequest model with Pydantic schema in src/models/approval_request.py"
Task: "Create SkillDefinition model with Pydantic schema in src/models/skill_definition.py"
Task: "Create WatcherConfig model with Pydantic schema in src/models/watcher_config.py"

# Launch all utility creation tasks together:
Task: "Create atomic file write utility in src/utils/file_ops.py"
Task: "Create markdown parser utility in src/utils/file_ops.py"
Task: "Create schema validator utility in src/utils/validators.py"
```

## Parallel Example: Phase 3 (US1+US2)

```bash
# Launch skill implementations in parallel:
Task: "Create Logging & Audit skill implementation in src/skills/logging_audit.py"
Task: "Create Approval Guard skill implementation in src/skills/approval_guard.py"

# Launch SKILL.md documentation in parallel:
Task: "Create Task Orchestrator SKILL.md in .claude/skills/task-orchestrator/SKILL.md"
Task: "Create Approval Guard SKILL.md in .claude/skills/approval-guard/SKILL.md"
Task: "Create Logging & Audit SKILL.md in .claude/skills/logging-audit/SKILL.md"
```

---

## Implementation Strategy

### MVP First (User Stories 1+2 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T021) - CRITICAL
3. Complete Phase 3: User Stories 1+2 (T022-T040)
4. **STOP and VALIDATE**: Test core orchestration independently
   - Create low-risk task → verify auto-execution and logging
   - Create high-risk task → verify approval request creation and blocking
   - Manually approve → verify execution proceeds
   - Check all actions logged in Logs/YYYY-MM-DD.json
5. Deploy/demo if ready - this is a functional Bronze Tier FTE

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Stories 1+2 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 3 → Test independently → Deploy/Demo (now proactive)
4. Add User Story 4 → Test independently → Deploy/Demo (now persistent)
5. Add User Story 5 → Test independently → Deploy/Demo (now manageable)
6. Add Polish → Final validation → Deploy/Demo (production ready)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T021)
2. **Once Foundational is done:**
   - Developer A: User Stories 1+2 (T022-T040) - Core MVP
   - Developer B: User Story 3 (T041-T048) - Proactive monitoring
   - Developer C: User Story 5 (T057-T065) - Skill management
3. **After US1+US2 completes:**
   - Developer A: User Story 4 (T049-T056) - Persistence
4. **All developers:** Polish phase (T066-T078)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **US1+US2 combined**: These stories are tightly coupled and must work together
- **Each user story should be independently testable** after completion
- **Commit after each task** or logical group for easy rollback
- **Stop at any checkpoint** to validate story independently
- **DRY_RUN mode**: Use throughout development for safe testing
- **Constitutional compliance**: Verify at each checkpoint

## Bronze Tier Graduation Checklist

After completing all tasks, verify:

- [ ] AI_Employee_Vault/ fully structured with all directories
- [ ] 3 skills exist in .claude/skills/ with valid SKILL.md files
- [ ] main.py acts as orchestrator with continuous loop
- [ ] Logs generated for all actions in Logs/YYYY-MM-DD.json
- [ ] Approval system blocks high-risk actions
- [ ] One workflow fully automated (file watcher → draft reply)
- [ ] DRY_RUN mode respected throughout
- [ ] Persistence loop continues until task in Done/
- [ ] All constitutional principles enforced
- [ ] System passes quickstart.md validation

---

**Total Tasks**: 78
**MVP Tasks** (Setup + Foundational + US1+US2): 40 tasks
**Parallel Opportunities**: 25+ tasks can run in parallel across phases
**Estimated MVP Completion**: Setup (8 tasks) + Foundational (13 tasks) + US1+US2 (19 tasks) = 40 tasks for working Bronze Tier FTE
