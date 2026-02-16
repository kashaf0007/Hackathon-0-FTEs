---
id: 001
title: Create Bronze Tier FTE Spec
stage: spec
date: 2026-02-16
surface: agent
model: claude-sonnet-4-5
feature: bronze-tier-fte
branch: 001-bronze-tier-fte
user: user
command: /sp.specify
labels: ["bronze-tier", "constitutional-fte", "specification", "hackathon"]
links:
  spec: specs/001-bronze-tier-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier-fte/spec.md
  - specs/001-bronze-tier-fte/checklists/requirements.md
tests:
  - None (specification phase)
---

## Prompt

User requested creation of Bronze Tier Constitutional FTE specification with the following requirements:

**Bronze Tier Purpose**: Minimum Viable Constitutional FTE

**Core Principles**: Local-First, HITL (Human-in-the-Loop), Proactivity, Persistence, Transparency, Cost Efficiency

**Mandatory Architecture**:
- Directory structure: /Business_Goals.md, /Dashboard.md, /Logs/, /Pending_Approval/, /Briefings/, /Done/, /Needs_Action/, .claude/skills/
- Constitutional enforcement for all principles
- Structured skills under .claude/skills/skill-name/SKILL.md

**Required Bronze Skills** (minimum 3):
1. Task Orchestrator Skill - Manage multi-step tasks using Plan.md, track status, move completed tasks to /Done/, log state transitions
2. Approval Guard Skill - Enforce autonomy levels, evaluate risk, create approval requests, block execution until approved
3. Logging & Audit Skill - Log every action to /Logs/YYYY-MM-DD.json with complete metadata, flag constitutional violations

**SKILL.md Required Schema**: Purpose, Constitutional Alignment, Inputs, Outputs, Risk Classification, Execution Logic, HITL Checkpoint, Logging Requirements, Failure Handling, Completion Condition

**Required Workflow**: Demonstrate at least one complete autonomous workflow (Email → Task → Plan → Completion example provided)

**Autonomy Level**: Bronze = Level 1 Controlled Autonomy
- Can draft emails automatically
- Limited email sending
- Draft-only social media posts
- Cannot execute payments, delete files, or multi-agent collaboration

**Security Requirements**: .env.example, DRY_RUN support, no plain-text credentials, local storage only, monthly credential rotation reminder

**Evaluation Criteria**: Constitutional Compliance (30%), Skill Structure Quality (20%), HITL Enforcement (15%), Logging Transparency (15%), Workflow Automation (10%), Documentation Clarity (10%)

## Response snapshot

Created comprehensive specification for Bronze Tier Constitutional FTE system:

**Branch Created**: 001-bronze-tier-fte

**Specification File**: specs/001-bronze-tier-fte/spec.md
- 5 prioritized user stories (P1: Autonomous execution with safety, Transparency/logging; P2: Proactive monitoring, Persistence; P3: Skill management)
- 36 functional requirements organized by category (Constitutional Principles, Directory Structure, Required Skills, Schema Compliance, Workflow, Autonomy Constraints, Security)
- 10 measurable success criteria (technology-agnostic, user-focused)
- 8 edge cases identified
- 5 key entities defined (Task, Approval Request, Log Entry, Skill Definition, Watcher)
- Comprehensive sections: Assumptions, Dependencies, Out of Scope, Constraints, Risks with mitigations

**Quality Checklist**: specs/001-bronze-tier-fte/checklists/requirements.md
- All validation checks passed
- No [NEEDS CLARIFICATION] markers needed
- Specification ready for /sp.plan phase

**Key Design Decisions**:
- Polling mechanism for watchers (not real-time streaming)
- JSON format for structured logs
- Manual approval workflow via file editing
- Simple retry strategy for Bronze tier
- File-based dashboard (no web UI required)

## Outcome

- ✅ Impact: Complete specification created for Bronze Tier Constitutional FTE with all mandatory requirements, constitutional principles, and evaluation criteria addressed
- 🧪 Tests: Specification validation checklist created and passed (Content Quality, Requirement Completeness, Feature Readiness)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.clarify (if needed), /sp.plan (architectural design), /sp.tasks (task generation), /sp.implement (execution)
- 🧠 Reflection: Specification successfully balances constitutional compliance requirements with practical Bronze tier constraints. All six core principles (Local-First, HITL, Proactivity, Persistence, Transparency, Cost Efficiency) mapped to functional requirements. Informed assumptions documented for implementation flexibility.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification creation completed successfully on first attempt
- Graders run and results (PASS/FAIL): Specification Quality Checklist - PASS (all 13 validation items passed)
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive Bronze Tier requirements
- Next experiment (smallest change to try): Proceed to /sp.plan to validate that specification provides sufficient detail for architectural design without requiring clarifications
