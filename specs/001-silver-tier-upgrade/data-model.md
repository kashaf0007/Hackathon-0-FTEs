# Data Model: Silver Tier

**Feature**: Silver Tier - Functional Business Assistant
**Date**: 2026-02-17
**Status**: Design Phase

## Overview

This document defines all data entities, schemas, state machines, and validation rules for Silver Tier. All entities use file-based storage with JSON or Markdown formats.

## Entity Schemas

### 1. Event (Watcher Output)

**Purpose**: Standardized format for all detected events from watchers

**Storage**: `AI_Employee_Vault/Needs_Action/{event_id}.json`

**Schema**:
```json
{
  "event_id": "string (YYYYMMDD_HHMMSS_source_uuid)",
  "source": "string (gmail|whatsapp|linkedin|filesystem)",
  "type": "string (new_message|new_email|connection_request|file_change)",
  "timestamp": "string (ISO 8601)",
  "priority": "string (low|medium|high|urgent)",
  "content": {
    "subject": "string (optional)",
    "body": "string",
    "from": "string (sender identifier)",
    "to": "string (recipient identifier)",
    "attachments": ["array of attachment metadata"]
  },
  "metadata": {
    "thread_id": "string (optional)",
    "labels": ["array of strings"],
    "is_reply": "boolean",
    "contact_history": "string (new|known|frequent)",
    "raw_data": "object (source-specific data)"
  },
  "created_at": "string (ISO 8601)",
  "processed": "boolean (default: false)"
}
```

**Validation Rules**:
- `event_id` must be unique
- `source` must be one of: gmail, whatsapp, linkedin, filesystem
- `type` must be valid for the source
- `timestamp` must be valid ISO 8601 format
- `priority` must be one of: low, medium, high, urgent
- `content.body` is required
- `created_at` must be valid ISO 8601 format

**Example**:
```json
{
  "event_id": "20260217_143022_gmail_a3f2c1",
  "source": "gmail",
  "type": "new_email",
  "timestamp": "2026-02-17T14:30:22Z",
  "priority": "medium",
  "content": {
    "subject": "Question about your services",
    "body": "Hi, I'm interested in learning more about your consulting services...",
    "from": "potential.client@example.com",
    "to": "me@example.com",
    "attachments": []
  },
  "metadata": {
    "thread_id": "thread_abc123",
    "labels": ["INBOX", "UNREAD"],
    "is_reply": false,
    "contact_history": "new",
    "raw_data": {
      "message_id": "msg_xyz789"
    }
  },
  "created_at": "2026-02-17T14:30:25Z",
  "processed": false
}
```

---

### 2. Plan (Reasoning Loop Output)

**Purpose**: Structured execution plan for multi-step tasks

**Storage**: `AI_Employee_Vault/Plan.md` (single active plan) or `AI_Employee_Vault/plans/{plan_id}.md` (archived plans)

**Schema** (Markdown format):
```markdown
# Plan: {Plan Title}

**Plan ID**: {plan_id}
**Created**: {ISO 8601 timestamp}
**Status**: {pending|in_progress|completed|failed}
**Risk Level**: {low|medium|high}
**Requires Approval**: {yes|no}

## Objective

{Clear statement of what this plan aims to achieve}

## Context

{Background information, triggering event, relevant history}

## Proposed Actions

1. **Action 1**: {Description}
   - Status: {pending|in_progress|completed|failed}
   - Started: {timestamp or null}
   - Completed: {timestamp or null}
   - Result: {outcome description or null}

2. **Action 2**: {Description}
   - Status: {pending|in_progress|completed|failed}
   - Started: {timestamp or null}
   - Completed: {timestamp or null}
   - Result: {outcome description or null}

## Risk Assessment

- **Risk Level**: {low|medium|high}
- **Risk Factors**: {List of identified risks}
- **Mitigation**: {How risks are being addressed}

## Approval Status

- **Requires Approval**: {yes|no}
- **Approval Requested**: {timestamp or null}
- **Approval Granted**: {timestamp or null}
- **Approved By**: {human identifier or null}

## Execution Log

- {timestamp}: {Event description}
- {timestamp}: {Event description}

## Outcome

{Final result once plan is completed or failed}
```

**State Machine**:
```
pending → in_progress → completed
                     ↓
                   failed
```

**Validation Rules**:
- Plan ID must be unique
- Status must be one of: pending, in_progress, completed, failed
- Risk level must be one of: low, medium, high
- If risk level is medium or high, requires_approval must be yes
- Actions must be numbered sequentially
- Each action must have a status

---

### 3. Approval Request

**Purpose**: Request human approval for sensitive actions

**Storage**: `AI_Employee_Vault/Pending_Approval/{action_id}.md`

**Schema** (Markdown format):
```markdown
# Approval Request: {Action Type}

**Action ID**: {action_id}
**Risk Level**: {low|medium|high}
**Created**: {ISO 8601 timestamp}
**Expires**: {ISO 8601 timestamp (created + 24 hours)}
**Related Plan**: {plan_id or null}

## Description

{Detailed description of the action requiring approval}

## Risk Assessment

- **Risk Level**: {low|medium|high}
- **Risk Factors**:
  - {Risk factor 1}
  - {Risk factor 2}
- **Potential Impact**: {Description of what could go wrong}

## Action Details

- **Type**: {email_send|linkedin_post|payment|file_delete|etc}
- **Target**: {Who/what will be affected}
- **Content**: {Preview of content/action}

## Instructions

To approve this action:
1. Review the description and risk assessment above
2. Move this file to: `AI_Employee_Vault/Approved/`
3. The system will execute the action automatically

To reject this action:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel the action

**Timeout**: This request will expire in 24 hours if not approved.

## Metadata

```json
{
  "action_id": "{action_id}",
  "action_type": "{type}",
  "risk_level": "{level}",
  "created_at": "{timestamp}",
  "expires_at": "{timestamp}",
  "plan_id": "{plan_id or null}",
  "action_data": {
    // Action-specific data
  }
}
```
```

**State Machine**:
```
pending → approved → executed
       ↓
       rejected
       ↓
       timeout (auto-reject after 24h)
```

**Validation Rules**:
- Action ID must be unique
- Risk level must be one of: low, medium, high
- Created timestamp must be valid ISO 8601
- Expires timestamp must be created + 24 hours
- Action type must be valid
- Metadata JSON must be valid

---

### 4. Log Entry

**Purpose**: Audit trail for all system actions

**Storage**: `AI_Employee_Vault/Logs/{YYYY-MM-DD}.json`

**Schema**:
```json
{
  "date": "YYYY-MM-DD",
  "entries": [
    {
      "timestamp": "string (ISO 8601 with milliseconds)",
      "level": "string (info|warning|error)",
      "component": "string (watcher|skill|mcp|orchestrator)",
      "action": "string (action type)",
      "actor": "string (component name)",
      "target": "string (what was acted upon)",
      "status": "string (success|failure|pending)",
      "details": {
        "event_id": "string (optional)",
        "plan_id": "string (optional)",
        "action_id": "string (optional)",
        "error_message": "string (optional)",
        "metadata": "object (action-specific data)"
      },
      "duration_ms": "number (optional)"
    }
  ]
}
```

**Validation Rules**:
- Date must be YYYY-MM-DD format
- Timestamp must be ISO 8601 with milliseconds
- Level must be one of: info, warning, error
- Component must be one of: watcher, skill, mcp, orchestrator
- Status must be one of: success, failure, pending
- All entries for a given date must be in the same file

**Example**:
```json
{
  "date": "2026-02-17",
  "entries": [
    {
      "timestamp": "2026-02-17T14:30:25.123Z",
      "level": "info",
      "component": "watcher",
      "action": "event_detected",
      "actor": "gmail_watcher",
      "target": "potential.client@example.com",
      "status": "success",
      "details": {
        "event_id": "20260217_143022_gmail_a3f2c1",
        "event_type": "new_email",
        "metadata": {
          "subject": "Question about your services"
        }
      },
      "duration_ms": 234
    }
  ]
}
```

---

### 5. Task File

**Purpose**: Completed or archived task records

**Storage**: `AI_Employee_Vault/Done/{task_id}.md`

**Schema** (Markdown format):
```markdown
# Task: {Task Title}

**Task ID**: {task_id}
**Source Event**: {event_id}
**Created**: {ISO 8601 timestamp}
**Completed**: {ISO 8601 timestamp}
**Status**: {completed|failed|cancelled}

## Original Event

{Summary of the triggering event}

## Plan Executed

{Link to plan file or summary of actions taken}

## Actions Taken

1. {Action 1 description} - {timestamp}
2. {Action 2 description} - {timestamp}

## Outcome

{Description of final result}

## Approvals

- {Approval 1}: Granted at {timestamp}
- {Approval 2}: Granted at {timestamp}

## Logs

- {timestamp}: {Log entry}
- {timestamp}: {Log entry}

## Metadata

```json
{
  "task_id": "{task_id}",
  "event_id": "{event_id}",
  "plan_id": "{plan_id}",
  "created_at": "{timestamp}",
  "completed_at": "{timestamp}",
  "status": "{status}",
  "actions_count": number,
  "approvals_count": number
}
```
```

---

### 6. Business Goals

**Purpose**: Strategic objectives and messaging guidelines for AI decision-making

**Storage**: `AI_Employee_Vault/Business_Goals.md`

**Schema** (Markdown format):
```markdown
# Business Goals

**Last Updated**: {ISO 8601 timestamp}
**Version**: {semantic version}

## Target Audience

{Description of ideal customers/clients}

## Key Messages

1. {Message 1}
2. {Message 2}
3. {Message 3}

## Value Proposition

{What makes the business unique}

## Content Guidelines

### Tone
- {Tone guideline 1}
- {Tone guideline 2}

### Topics to Emphasize
- {Topic 1}
- {Topic 2}

### Topics to Avoid
- {Topic 1}
- {Topic 2}

## Success Metrics

- {Metric 1}: {Target}
- {Metric 2}: {Target}

## Call-to-Action

{Preferred CTA for LinkedIn posts and outreach}

## Brand Voice

{Description of brand personality and communication style}
```

---

### 7. Dashboard

**Purpose**: Current system status and activity summary

**Storage**: `AI_Employee_Vault/Dashboard.md`

**Schema** (Markdown format):
```markdown
# AI Employee Dashboard

**Last Updated**: {ISO 8601 timestamp}
**System Status**: {operational|degraded|offline}

## Active Tasks

| Task ID | Type | Status | Created | Priority |
|---------|------|--------|---------|----------|
| {id} | {type} | {status} | {timestamp} | {priority} |

## Pending Approvals

| Action ID | Type | Risk | Created | Expires |
|-----------|------|------|---------|---------|
| {id} | {type} | {level} | {timestamp} | {timestamp} |

## Recent Completions (Last 7 Days)

| Task ID | Type | Completed | Outcome |
|---------|------|-----------|---------|
| {id} | {type} | {timestamp} | {summary} |

## System Health

- **Watchers**: {count} active, last run {timestamp}
- **MCP Servers**: {count} operational
- **Logs**: {count} entries today
- **Errors**: {count} in last 24 hours

## Weekly Summary

- **Events Detected**: {count}
- **Tasks Completed**: {count}
- **Approvals Requested**: {count}
- **Approvals Granted**: {count}
- **LinkedIn Posts**: {count}
- **Emails Sent**: {count}

## Alerts

- {Alert 1 if any}
- {Alert 2 if any}

## Next Scheduled Actions

- {Action 1}: {timestamp}
- {Action 2}: {timestamp}
```

---

## State Machines

### Event Processing State Machine

```
[Watcher Detects Event]
         ↓
[Create Event File in Needs_Action/]
         ↓
[Reasoning Loop Picks Up Event]
         ↓
[Generate Plan.md]
         ↓
[Risk Classification]
         ↓
    ┌────┴────┐
    ↓         ↓
[Low Risk] [Medium/High Risk]
    ↓         ↓
[Execute] [Create Approval Request]
    ↓         ↓
    │    [Wait for Approval]
    │         ↓
    │    ┌────┴────┐
    │    ↓         ↓
    │ [Approved] [Rejected/Timeout]
    │    ↓         ↓
    └──→[Execute] [Cancel]
         ↓         ↓
    [Move to Done/] [Log & Archive]
```

### Approval Workflow State Machine

```
[Action Requires Approval]
         ↓
[Create Approval File in Pending_Approval/]
         ↓
[Notify Human (optional)]
         ↓
[Poll for File Movement]
         ↓
    ┌────┴────┐
    ↓         ↓
[File in Approved/] [File in Rejected/ OR Timeout]
    ↓         ↓
[Execute Action] [Cancel Action]
    ↓         ↓
[Move to Done/] [Log Cancellation]
```

### Plan Execution State Machine

```
[Plan Created (pending)]
         ↓
[Start Execution (in_progress)]
         ↓
[Execute Action 1]
         ↓
[Update Plan.md with Result]
         ↓
[Execute Action 2]
         ↓
[Update Plan.md with Result]
         ↓
    ┌────┴────┐
    ↓         ↓
[All Actions Complete] [Action Failed]
    ↓         ↓
[Plan Status: completed] [Plan Status: failed]
    ↓         ↓
[Move to Done/] [Log Error & Archive]
```

---

## Validation Rules Summary

### File Naming Conventions

- Event files: `{YYYYMMDD_HHMMSS}_{source}_{uuid}.json`
- Plan files: `{YYYYMMDD_HHMMSS}_{plan_title_slug}.md`
- Approval files: `{action_id}.md`
- Log files: `{YYYY-MM-DD}.json`
- Task files: `{task_id}.md`

### Required Fields by Entity

| Entity | Required Fields |
|--------|----------------|
| Event | event_id, source, type, timestamp, priority, content.body, created_at |
| Plan | plan_id, created, status, risk_level, objective, actions |
| Approval | action_id, risk_level, created, expires, description |
| Log Entry | timestamp, level, component, action, actor, status |
| Task | task_id, source_event, created, completed, status, outcome |

### Enum Values

| Field | Valid Values |
|-------|-------------|
| event.source | gmail, whatsapp, linkedin, filesystem |
| event.priority | low, medium, high, urgent |
| plan.status | pending, in_progress, completed, failed |
| plan.risk_level | low, medium, high |
| approval.risk_level | low, medium, high |
| log.level | info, warning, error |
| log.component | watcher, skill, mcp, orchestrator |
| log.status | success, failure, pending |
| task.status | completed, failed, cancelled |

---

## Data Integrity Rules

1. **Event ID Uniqueness**: No two events can have the same event_id
2. **Plan ID Uniqueness**: No two plans can have the same plan_id
3. **Action ID Uniqueness**: No two approval requests can have the same action_id
4. **Log Chronology**: Log entries within a file must be in chronological order
5. **File Atomicity**: All file writes must be atomic (write to temp, then rename)
6. **State Consistency**: Entity state must match file location (e.g., approved files in Approved/)
7. **Referential Integrity**: plan_id references in approvals must point to existing plans
8. **Timestamp Validity**: All timestamps must be valid ISO 8601 format
9. **Approval Timeout**: Approval requests older than 24 hours must be auto-rejected
10. **Log Rotation**: Log files older than 90 days should be archived

---

## Schema Evolution

### Version 1.0.0 (Current)
- Initial schema definitions
- All entities defined
- State machines documented

### Future Considerations
- Add support for recurring tasks
- Add support for task dependencies
- Add support for multi-step approvals
- Add support for approval delegation
- Add support for custom risk rules
- Add support for event aggregation

---

## Testing Data

### Sample Event (Gmail)
```json
{
  "event_id": "20260217_143022_gmail_test001",
  "source": "gmail",
  "type": "new_email",
  "timestamp": "2026-02-17T14:30:22Z",
  "priority": "medium",
  "content": {
    "subject": "Test Email",
    "body": "This is a test email for validation",
    "from": "test@example.com",
    "to": "me@example.com",
    "attachments": []
  },
  "metadata": {
    "thread_id": "thread_test001",
    "labels": ["INBOX"],
    "is_reply": false,
    "contact_history": "known",
    "raw_data": {}
  },
  "created_at": "2026-02-17T14:30:25Z",
  "processed": false
}
```

### Sample Approval Request
```markdown
# Approval Request: LinkedIn Post

**Action ID**: linkedin_post_20260217_001
**Risk Level**: medium
**Created**: 2026-02-17T15:00:00Z
**Expires**: 2026-02-18T15:00:00Z
**Related Plan**: plan_20260217_001

## Description

Post to LinkedIn about new consulting services offering.

## Risk Assessment

- **Risk Level**: medium
- **Risk Factors**:
  - Public post visible to all connections
  - Represents company brand
- **Potential Impact**: Brand reputation if content is inappropriate

## Action Details

- **Type**: linkedin_post
- **Target**: LinkedIn profile
- **Content**: "Excited to announce our new AI consulting services..."

## Instructions

[Standard approval instructions]
```

---

## Next Steps

1. Create contracts/ directory with MCP server specifications
2. Create quickstart.md with setup and testing procedures
3. Implement validation functions for each entity
4. Create test fixtures based on sample data
5. Generate tasks.md for implementation
