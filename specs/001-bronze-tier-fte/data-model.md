# Data Model: Bronze Tier Constitutional FTE

**Feature**: Bronze Tier Constitutional FTE
**Date**: 2026-02-16
**Phase**: 1 (Data Model & Contracts)

## Overview

This document defines the core entities, their schemas, relationships, and validation rules for the Bronze Tier Constitutional FTE system. All entities use Pydantic models for runtime validation and JSON schemas for contract documentation.

## Entity Relationships

```
┌─────────────────┐
│  Task           │
│  (Needs_Action) │
└────────┬────────┘
         │
         │ triggers
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Task Orchestrator│─────▶│ Approval Request │
│ (processes)      │      │ (if HIGH risk)   │
└────────┬────────┘      └──────────────────┘
         │
         │ evaluates via
         ▼
┌─────────────────┐
│ Approval Guard  │
│ (risk check)    │
└────────┬────────┘
         │
         │ logs to
         ▼
┌─────────────────┐
│ Log Entry       │
│ (audit trail)   │
└─────────────────┘
         │
         │ references
         ▼
┌─────────────────┐
│ Skill Definition│
│ (capabilities)  │
└─────────────────┘
```

## Core Entities

### 1. Task

**Purpose**: Represents a unit of work to be executed by the orchestrator.

**Location**: `AI_Employee_Vault/Needs_Action/*.md` (pending), `AI_Employee_Vault/Done/*.md` (completed)

**Schema** (Pydantic):
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Dict, Any

class Task(BaseModel):
    """Task entity for work items"""
    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Human-readable task title")
    type: str = Field(..., description="Task type (e.g., draft_email, organize_files)")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(default="MEDIUM")
    status: Literal["PENDING", "IN_PROGRESS", "AWAITING_APPROVAL", "APPROVED", "COMPLETED", "FAILED"] = Field(default="PENDING")
    created: datetime = Field(default_factory=datetime.now)
    updated: Optional[datetime] = None
    completed: Optional[datetime] = None
    assigned_skill: Optional[str] = Field(None, description="Skill handling this task")
    retry_count: int = Field(default=0, ge=0, le=3)
    context: Dict[str, Any] = Field(default_factory=dict, description="Task-specific context data")
    expected_output: Optional[str] = Field(None, description="Description of expected result")
    actual_output: Optional[str] = Field(None, description="Actual result after execution")
    error_message: Optional[str] = Field(None, description="Error details if failed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Validation Rules**:
- `task_id` must be unique across all tasks
- `retry_count` cannot exceed 3
- `completed` timestamp only set when status is COMPLETED or FAILED
- `error_message` only populated when status is FAILED
- `assigned_skill` must reference valid skill in .claude/skills/

**State Transitions**:
```
PENDING → IN_PROGRESS → COMPLETED
                      → FAILED
                      → AWAITING_APPROVAL → APPROVED → IN_PROGRESS
```

**File Format** (Markdown):
```markdown
# Task: [Title]

**Type**: [type]
**Priority**: [LOW|MEDIUM|HIGH]
**Created**: [ISO 8601 timestamp]
**Status**: [status]

## Context
[Task-specific context and details]

## Expected Output
[Description of what should be produced]

## Actual Output
[Populated after execution]
```

### 2. Log Entry

**Purpose**: Records every action taken by the system for audit trail and transparency.

**Location**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

**Schema** (Pydantic):
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Dict, Any

class LogEntry(BaseModel):
    """Log entry for audit trail"""
    timestamp: datetime = Field(default_factory=datetime.now)
    task_id: Optional[str] = Field(None, description="Associated task ID")
    action: str = Field(..., description="Action performed")
    skill_used: Optional[str] = Field(None, description="Skill that performed action")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(...)
    approval_status: Literal["AUTO_APPROVED", "PENDING_APPROVAL", "APPROVED", "REJECTED"] = Field(...)
    outcome: Literal["SUCCESS", "FAILURE", "BLOCKED"] = Field(...)
    error: Optional[str] = Field(None, description="Error message if failed")
    constitutional_compliance: bool = Field(default=True, description="Whether action complies with constitution")
    dry_run: bool = Field(default=False, description="Whether this was a simulated action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Validation Rules**:
- `timestamp` must be in UTC
- `error` only populated when outcome is FAILURE
- `constitutional_compliance` must be True unless violation detected
- `metadata` should include: duration_ms, retry_count, user_agent

**File Format** (JSON Array):
```json
[
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
    "dry_run": false,
    "metadata": {
      "duration_ms": 150,
      "retry_count": 0
    }
  }
]
```

### 3. Approval Request

**Purpose**: Represents a high-risk action awaiting human approval.

**Location**: `AI_Employee_Vault/Pending_Approval/*.md`

**Schema** (Pydantic):
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class ApprovalRequest(BaseModel):
    """Approval request for high-risk actions"""
    request_id: str = Field(..., description="Unique request identifier")
    task_id: str = Field(..., description="Associated task ID")
    action: str = Field(..., description="Action requiring approval")
    risk_level: Literal["MEDIUM", "HIGH"] = Field(...)
    justification: str = Field(..., description="Why this action is needed")
    impact: str = Field(..., description="What will happen if approved")
    created: datetime = Field(default_factory=datetime.now)
    status: Literal["PENDING", "APPROVED", "REJECTED"] = Field(default="PENDING")
    approver: Optional[str] = Field(None, description="Who approved/rejected")
    decision_time: Optional[datetime] = None
    notes: Optional[str] = Field(None, description="Approver notes")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Validation Rules**:
- `request_id` must be unique
- `task_id` must reference existing task
- `risk_level` must be MEDIUM or HIGH (LOW doesn't require approval)
- `approver` and `decision_time` only set when status is APPROVED or REJECTED
- Requests older than 7 days should trigger warning

**File Format** (Markdown):
```markdown
# Approval Request: [Request ID]

**Task ID**: [task_id]
**Created**: [ISO 8601 timestamp]
**Risk Level**: [MEDIUM|HIGH]
**Action**: [action description]

## Justification
[Why this action is needed]

## Impact
[What will happen if approved]

## Approval
**Status**: [PENDING|APPROVED|REJECTED]
**Approver**: [leave blank until decided]
**Decision**: [APPROVE|REJECT]
**Notes**: [optional approver notes]
```

### 4. Skill Definition

**Purpose**: Defines a capability of the FTE with metadata and execution logic.

**Location**: `.claude/skills/[skill-name]/SKILL.md`

**Schema** (Pydantic):
```python
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any

class SkillDefinition(BaseModel):
    """Skill definition metadata"""
    name: str = Field(..., description="Skill name (matches directory name)")
    purpose: str = Field(..., description="What this skill does")
    constitutional_alignment: List[str] = Field(..., description="Which principles this enforces")
    inputs: List[str] = Field(..., description="What triggers this skill")
    outputs: List[str] = Field(..., description="Files created/modified")
    risk_classification: Literal["LOW", "MEDIUM", "HIGH"] = Field(...)
    execution_logic: str = Field(..., description="Step-by-step execution flow")
    hitl_checkpoint: str = Field(..., description="When approval is required")
    logging_requirements: str = Field(..., description="What must be logged")
    failure_handling: str = Field(..., description="What happens on error")
    completion_condition: str = Field(..., description="When task is complete")

    class Config:
        validate_assignment = True
```

**Validation Rules**:
- `name` must match directory name in .claude/skills/
- `constitutional_alignment` must reference valid principles from constitution
- All required sections must be non-empty
- `risk_classification` determines approval requirements

**File Format** (Markdown with required sections):
```markdown
# [Skill Name]

## Purpose
[Clear description of responsibility]

## Constitutional Alignment
[Which principles this skill enforces]

## Inputs
[What triggers this skill]

## Outputs
[Files created, moved, or updated]

## Risk Classification
[LOW | MEDIUM | HIGH]

## Execution Logic
[Step-by-step deterministic flow]

## HITL Checkpoint
[When approval is required]

## Logging Requirements
[What must be logged]

## Failure Handling
[What happens if error occurs]

## Completion Condition
[When TASK_COMPLETE is valid]
```

### 5. Watcher Configuration

**Purpose**: Defines a proactive monitoring system that creates tasks.

**Location**: Configuration embedded in watcher implementation (future: separate config file)

**Schema** (Pydantic):
```python
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

class WatcherConfig(BaseModel):
    """Watcher configuration"""
    name: str = Field(..., description="Watcher name")
    type: Literal["file", "email", "schedule"] = Field(...)
    enabled: bool = Field(default=True)
    trigger_conditions: Dict[str, Any] = Field(..., description="When to trigger")
    polling_interval: int = Field(default=60, ge=1, description="Seconds between checks")
    task_template: Dict[str, Any] = Field(..., description="Template for created tasks")

    class Config:
        validate_assignment = True
```

**Validation Rules**:
- `name` must be unique across watchers
- `polling_interval` must be positive integer
- `task_template` must include: type, priority, context structure

**Example Configuration**:
```python
file_watcher = WatcherConfig(
    name="demo-file-watcher",
    type="file",
    enabled=True,
    trigger_conditions={
        "path": "./monitored",
        "pattern": "*.txt",
        "event": "created"
    },
    polling_interval=5,
    task_template={
        "type": "draft_email",
        "priority": "MEDIUM",
        "context": {
            "source": "file_watcher"
        }
    }
)
```

## Entity Relationships

### Task → Approval Request (1:0..1)
- A task may create zero or one approval request
- Approval request references task via `task_id`
- Task status becomes AWAITING_APPROVAL when request created

### Task → Log Entry (1:N)
- A task generates multiple log entries throughout lifecycle
- Log entries reference task via `task_id`
- Minimum log entries: task_created, task_started, task_completed

### Task → Skill Definition (N:1)
- A task is processed by one skill
- Multiple tasks can use same skill
- Task references skill via `assigned_skill` field

### Approval Request → Log Entry (1:N)
- Approval request creation logged
- Approval decision logged
- Log entries reference request via metadata

## Data Validation Rules

### Cross-Entity Validation

1. **Task → Skill Reference**:
   - `task.assigned_skill` must exist in `.claude/skills/`
   - Skill must have valid SKILL.md with all required sections

2. **Task → Approval Request**:
   - If `task.status == AWAITING_APPROVAL`, approval request must exist
   - Approval request `task_id` must match existing task

3. **Log Entry → Task Reference**:
   - If `log_entry.task_id` is set, task must exist or have existed
   - Log entry timestamp must be >= task.created timestamp

4. **Approval Request Age**:
   - Requests older than 7 days trigger warning in Dashboard
   - Requests older than 30 days trigger escalation

### State Consistency Rules

1. **Task State Machine**:
   - Cannot transition from COMPLETED to any other state
   - Cannot transition from FAILED to IN_PROGRESS without retry
   - AWAITING_APPROVAL requires approval request to exist

2. **Approval Request State Machine**:
   - Cannot transition from APPROVED/REJECTED back to PENDING
   - Decision time must be set when status changes from PENDING

3. **Log Entry Immutability**:
   - Log entries are append-only (never modified)
   - Log files are immutable after day ends

## File System Layout

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── task-001.md          # Task (PENDING)
│   └── task-002.md          # Task (PENDING)
├── Pending_Approval/
│   └── approval-001.md      # Approval Request (PENDING)
├── Done/
│   ├── task-001.md          # Task (COMPLETED)
│   └── task-003.md          # Task (FAILED)
└── Logs/
    ├── 2026-02-16.json      # Log Entries (today)
    └── 2026-02-15.json      # Log Entries (yesterday)

.claude/skills/
├── task-orchestrator/
│   └── SKILL.md             # Skill Definition
├── approval-guard/
│   └── SKILL.md             # Skill Definition
└── logging-audit/
    └── SKILL.md             # Skill Definition
```

## Data Migration & Versioning

**Current Version**: 1.0.0 (initial schema)

**Future Considerations**:
- Add schema version field to all entities
- Implement migration scripts for schema changes
- Maintain backward compatibility for log files
- Archive old schema versions in docs/

## Summary

All core entities defined with Pydantic schemas, validation rules, and file formats. Relationships documented with clear referential integrity rules. Ready for contract generation (JSON schemas) and implementation.

**Next Steps**:
1. Generate JSON schemas in contracts/ directory
2. Create quickstart.md with setup instructions
3. Implement Pydantic models in src/models/
