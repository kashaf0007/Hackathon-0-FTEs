---
id: 002
title: Create Bronze Tier Architectural Plan
stage: plan
date: 2026-02-16
surface: agent
model: claude-sonnet-4-5
feature: bronze-tier-fte
branch: 001-bronze-tier-fte
user: Kashaf Aman
command: /sp.plan
labels: ["bronze-tier", "architecture", "planning", "constitutional-fte"]
links:
  spec: specs/001-bronze-tier-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier-fte/plan.md
  - specs/001-bronze-tier-fte/research.md
  - specs/001-bronze-tier-fte/data-model.md
  - specs/001-bronze-tier-fte/quickstart.md
  - specs/001-bronze-tier-fte/contracts/task-schema.json
  - specs/001-bronze-tier-fte/contracts/log-schema.json
  - specs/001-bronze-tier-fte/contracts/approval-schema.json
tests:
  - None (planning phase)
---

## Prompt

User provided comprehensive Bronze Tier Plan guidance with 10 phases for converting the repository into a Constitution-Compliant Digital FTE:

**Bronze Goal**: Convert repository into Constitution-Compliant Digital FTE using AI_Employee_Vault/ as operational vault, .claude/skills/ for structured skills, and main.py as orchestrator entrypoint.

**Key Phases Outlined**:
1. Restructure AI_Employee_Vault with constitutional directories (Business_Goals.md, Dashboard.md, Logs/, Pending_Approval/, Briefings/, Done/, Needs_Action/)
2. Create skills structure in .claude/skills/ (task-orchestrator, approval-guard, logging-audit)
3. Convert main.py to orchestrator with continuous loop (scan Needs_Action, load skills, run approval check, execute, log, move to Done)
4. Implement persistence layer (Ralph Wiggum principle - loop until Done or TASK_COMPLETE)
5. Implement HITL with approval boundaries (payments >$100, emotional emails, file deletion, new payees, DM replies)
6. Create logging system in Logs/YYYY-MM-DD.json with required fields (timestamp, task_id, skill_used, risk_level, approval_status, action_taken, result)
7. Add .env security (.env.example, .gitignore, DRY_RUN support)
8. Implement one workflow (Email → Task → Draft Reply demonstration)
9. Dashboard.md integration (Active Tasks, Pending Approvals, Completed Today, Violations)
10. Bronze testing checklist and definition of done

**Constitutional Principles to Enforce**: Local-First, HITL Safety, Proactivity, Persistence, Transparency, Cost Efficiency

## Response snapshot

Created comprehensive architectural plan with complete Phase 0 (Research) and Phase 1 (Data Model & Contracts) artifacts:

**Main Plan Document** (plan.md):
- Technical context: Python 3.11+, file-based storage, pytest testing, local platform
- Constitution Check: All 6 core principles validated, Bronze autonomy level compliance verified, security requirements met
- Project structure: AI_Employee_Vault/ operational workspace, .claude/skills/ definitions, src/ implementation
- Architecture overview: 5 system components (Orchestrator, Task Orchestrator Skill, Approval Guard Skill, Logging & Audit Skill, File Watcher)
- Data flow and state transitions documented
- 5 key design decisions with rationales (file-based queue, polling vs event-driven, skill format, log format, approval mechanism)
- Error handling strategy (transient vs permanent failures)
- Security considerations (credentials, file system, audit trail, DRY_RUN)

**Phase 0: Research Document** (research.md):
- Technology stack validation (Python 3.11+, python-dotenv, watchdog, pydantic, pytest)
- File system patterns (atomic writes, file locking, JSON log rotation, markdown parsing)
- DRY_RUN implementation pattern
- Polling vs event-driven architecture decision
- Skill loading pattern with schema validation
- All technical context items resolved (no NEEDS CLARIFICATION remaining)

**Phase 1: Data Model Document** (data-model.md):
- 5 core entities defined with Pydantic schemas: Task, Log Entry, Approval Request, Skill Definition, Watcher Configuration
- Entity relationships documented with cardinality
- Validation rules (cross-entity, state consistency, file system layout)
- State machines for Task and Approval Request
- File formats (Markdown for tasks/approvals, JSON for logs)
- Data migration and versioning strategy

**Phase 1: JSON Schema Contracts** (contracts/):
- task-schema.json: Task entity validation with required fields, enums, patterns
- log-schema.json: Log Entry validation with timestamp, risk levels, outcomes
- approval-schema.json: Approval Request validation with status workflow

**Phase 1: Quickstart Guide** (quickstart.md):
- Installation steps (virtual environment, dependencies, directory structure)
- Configuration guide (.env setup, vault initialization)
- Running the orchestrator with expected output
- Creating first task walkthrough
- Testing high-risk actions with approval flow
- Demo workflow: Email → Draft Reply
- Troubleshooting section
- Bronze Tier graduation checklist
- File templates and naming conventions

**Constitution Check Results**:
- Phase 0 Gate: ✅ PASS - All constitutional principles addressed
- Phase 1 Gate: ✅ PASS - Data model supports all constitutional requirements

## Outcome

- ✅ Impact: Complete architectural plan created with all Phase 0 and Phase 1 artifacts. System design fully aligned with Bronze Tier requirements and constitutional principles.
- 🧪 Tests: Planning phase complete - implementation and testing will occur in Phase 2 (/sp.tasks and /sp.implement)
- 📁 Files: 7 files created (plan.md, research.md, data-model.md, quickstart.md, 3 JSON schemas)
- 🔁 Next prompts: /sp.tasks (generate implementation tasks), /sp.implement (execute implementation), /sp.adr (document architectural decisions if needed)
- 🧠 Reflection: Architectural plan successfully integrates user's Bronze Tier guidance with constitutional requirements. Key decisions documented with rationales. File-based architecture chosen for transparency and local-first operation. Polling architecture selected for Bronze tier simplicity. All 10 phases from user guidance mapped to concrete implementation plan.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): Constitution Check Phase 0 - PASS, Constitution Check Phase 1 - PASS
- Prompt variant (if applicable): Standard /sp.plan workflow enhanced with Bronze Tier specific guidance
- Next experiment (smallest change to try): Proceed to /sp.tasks to validate that plan provides sufficient detail for task generation without ambiguity. Monitor whether 5-component architecture (Orchestrator, 3 Skills, Watcher) is sufficient or requires additional components during implementation.
