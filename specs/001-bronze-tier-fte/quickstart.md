# Quickstart Guide: Bronze Tier Constitutional FTE

**Feature**: Bronze Tier Constitutional FTE
**Version**: 1.0.0
**Date**: 2026-02-16

## Overview

This guide will help you set up and run the Bronze Tier Constitutional FTE system in under 10 minutes. By the end, you'll have a working autonomous orchestrator that monitors tasks, enforces approval boundaries, and logs all operations.

## Prerequisites

- Python 3.11 or higher
- Git (for version control)
- Text editor (VS Code, Sublime, etc.)
- Terminal/Command Prompt access

## Installation

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd AI-Employee-Hackathon

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies (after implementation)
pip install -e .
```

### Step 2: Create Directory Structure

```bash
# Create AI_Employee_Vault structure
mkdir -p AI_Employee_Vault/{Logs,Pending_Approval,Briefings,Done,Needs_Action}

# Create skills structure
mkdir -p .claude/skills/{task-orchestrator,approval-guard,logging-audit}

# Create source structure
mkdir -p src/{orchestrator,skills,models,watchers,utils}
mkdir -p tests/{unit,integration,fixtures}
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required variables:
# DRY_RUN=true  # Set to false for production
# LOG_LEVEL=INFO
```

**Example .env file**:
```env
# Bronze Tier FTE Configuration
DRY_RUN=true
LOG_LEVEL=INFO
POLL_INTERVAL=5
MAX_RETRIES=3
```

### Step 4: Initialize Vault Files

Create initial vault files:

**AI_Employee_Vault/Business_Goals.md**:
```markdown
# Business Goals

## Primary Objectives
- Automate routine task processing
- Maintain transparency through comprehensive logging
- Enforce safety boundaries for high-risk actions

## Success Metrics
- 100% of actions logged
- Zero unauthorized high-risk actions
- <5 second task detection latency
```

**AI_Employee_Vault/Dashboard.md**:
```markdown
# Dashboard

**Last Updated**: [Auto-generated]

## Status
- Active Tasks: 0
- Pending Approvals: 0
- Completed Today: 0
- Constitutional Violations: 0

## Recent Activity
[Auto-generated from logs]
```

## Running the System

### Start the Orchestrator

```bash
# Activate virtual environment if not already active
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run orchestrator
python -m src.orchestrator.main
```

**Expected Output**:
```
[2026-02-16 14:30:00] INFO: Bronze Tier FTE Orchestrator starting...
[2026-02-16 14:30:00] INFO: DRY_RUN mode: True
[2026-02-16 14:30:00] INFO: Loading skills from .claude/skills/
[2026-02-16 14:30:00] INFO: Loaded 3 skills: task-orchestrator, approval-guard, logging-audit
[2026-02-16 14:30:00] INFO: Starting orchestrator loop (poll interval: 5s)
[2026-02-16 14:30:00] INFO: Monitoring AI_Employee_Vault/Needs_Action/
```

### Create Your First Task

While the orchestrator is running, create a task file:

**AI_Employee_Vault/Needs_Action/task-001.md**:
```markdown
# Task: Draft Welcome Email

**Type**: draft_email
**Priority**: MEDIUM
**Created**: 2026-02-16T14:30:00Z
**Status**: PENDING

## Context
Draft a welcome email for new team members introducing the Bronze Tier FTE system.

## Expected Output
Email draft with subject, body, and key points about the system.
```

**What Happens Next**:
1. Orchestrator detects new task (within 5 seconds)
2. Task Orchestrator skill parses the task
3. Approval Guard evaluates risk (LOW for drafting)
4. Task executes (draft created)
5. Logging & Audit records action
6. Task moves to Done/

### Check the Logs

```bash
# View today's log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Or use jq for pretty printing
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'
```

**Example Log Entry**:
```json
{
  "timestamp": "2026-02-16T14:30:05Z",
  "task_id": "task-001",
  "action": "draft_email",
  "skill_used": "task-orchestrator",
  "risk_level": "LOW",
  "approval_status": "AUTO_APPROVED",
  "outcome": "SUCCESS",
  "constitutional_compliance": true,
  "dry_run": true,
  "metadata": {
    "duration_ms": 150,
    "retry_count": 0
  }
}
```

## Testing High-Risk Actions

### Create a High-Risk Task

**AI_Employee_Vault/Needs_Action/task-002.md**:
```markdown
# Task: Delete Old Files

**Type**: delete_file
**Priority**: LOW
**Created**: 2026-02-16T14:35:00Z
**Status**: PENDING

## Context
Delete temporary files older than 30 days from the archive directory.

## Expected Output
List of deleted files.
```

**What Happens**:
1. Orchestrator detects task
2. Approval Guard evaluates risk (HIGH for deletion)
3. Approval request created in Pending_Approval/
4. Task status becomes AWAITING_APPROVAL
5. Execution BLOCKED until approval

### Approve the Task

Edit the approval file:

**AI_Employee_Vault/Pending_Approval/approval-001.md**:
```markdown
# Approval Request: approval-001

**Task ID**: task-002
**Created**: 2026-02-16T14:35:05Z
**Risk Level**: HIGH
**Action**: delete_file

## Justification
Cleanup old temporary files to free disk space.

## Impact
Files older than 30 days will be permanently deleted.

## Approval
**Status**: APPROVED  # Change from PENDING to APPROVED
**Approver**: John Doe
**Decision**: APPROVE
**Notes**: Verified files are temporary and safe to delete.
```

**What Happens Next**:
1. Orchestrator detects approval
2. Task status changes to APPROVED
3. Task executes (files deleted)
4. Logging records approval and execution
5. Task moves to Done/

## Demo Workflow: Email → Draft Reply

### Setup File Watcher (Optional)

The demo workflow uses a file watcher to simulate email arrival:

```bash
# Create monitored directory
mkdir -p monitored

# Start orchestrator (if not already running)
python -m src.orchestrator.main
```

### Trigger the Workflow

```bash
# Simulate email arrival by creating a file
echo "Subject: Question about Bronze Tier
From: user@example.com

How does the approval system work?" > monitored/email-001.txt
```

**Workflow Execution**:
1. File watcher detects new file
2. Creates task in Needs_Action/
3. Task Orchestrator processes task
4. Approval Guard evaluates (LOW risk for drafting)
5. Draft reply generated
6. Logging records all steps
7. Task moves to Done/

**Check the Result**:
```bash
cat AI_Employee_Vault/Done/task-*.md
```

## Troubleshooting

### Orchestrator Won't Start

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### Tasks Not Being Processed

**Problem**: Tasks remain in Needs_Action/

**Solution**:
1. Check orchestrator is running: `ps aux | grep orchestrator`
2. Check file permissions: `ls -la AI_Employee_Vault/Needs_Action/`
3. Check logs for errors: `tail -f logs/orchestrator.log`

### Approval Not Working

**Problem**: Task stuck in AWAITING_APPROVAL

**Solution**:
1. Verify approval file exists: `ls AI_Employee_Vault/Pending_Approval/`
2. Check approval file format (Status: APPROVED, Decision: APPROVE)
3. Ensure approver name is filled in

### Logs Not Being Created

**Problem**: No log files in Logs/

**Solution**:
1. Check directory permissions: `ls -la AI_Employee_Vault/Logs/`
2. Check DRY_RUN mode (logs still created in dry run)
3. Verify logging skill is loaded: check orchestrator startup output

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DRY_RUN | false | Simulate actions without executing |
| LOG_LEVEL | INFO | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| POLL_INTERVAL | 5 | Seconds between task queue checks |
| MAX_RETRIES | 3 | Maximum retry attempts for failed tasks |

### Skill Configuration

Skills are configured via SKILL.md files in `.claude/skills/[skill-name]/`.

To modify skill behavior:
1. Edit the SKILL.md file
2. Restart orchestrator to reload skills

## Next Steps

### After Setup

1. **Review Constitution**: Read `.specify/memory/constitution.md` to understand principles
2. **Explore Skills**: Review skill definitions in `.claude/skills/`
3. **Create Custom Tasks**: Experiment with different task types
4. **Monitor Logs**: Use logs to understand system behavior
5. **Test Approval Flow**: Create high-risk tasks and practice approval workflow

### Advanced Usage

1. **Create Custom Skills**: Add new skills following SKILL.md schema
2. **Add Watchers**: Implement additional watchers for email, schedule, etc.
3. **Integrate Tools**: Connect external tools via MCP servers (Silver/Gold tier)
4. **Automate Workflows**: Chain multiple tasks for complex operations

### Production Deployment

Before using in production:

1. **Disable DRY_RUN**: Set `DRY_RUN=false` in .env
2. **Configure Credentials**: Add real credentials to .env
3. **Setup Monitoring**: Monitor logs and dashboard regularly
4. **Test Thoroughly**: Run full test suite with `pytest`
5. **Review Security**: Audit .gitignore, file permissions, credential storage

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_skills.py

# Run integration tests only
pytest tests/integration/
```

### Manual Testing Checklist

- [ ] Create low-risk task → auto-executes
- [ ] Create high-risk task → creates approval request
- [ ] Approve high-risk task → executes after approval
- [ ] Reject high-risk task → task cancelled
- [ ] Task with error → retries up to 3 times
- [ ] Task completes → moves to Done/
- [ ] All actions logged → check Logs/
- [ ] DRY_RUN mode → simulates without executing

## Support

### Documentation

- **Specification**: `specs/001-bronze-tier-fte/spec.md`
- **Architecture**: `specs/001-bronze-tier-fte/plan.md`
- **Data Model**: `specs/001-bronze-tier-fte/data-model.md`
- **Constitution**: `.specify/memory/constitution.md`

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

### Getting Help

1. Check logs: `AI_Employee_Vault/Logs/`
2. Review documentation in `specs/001-bronze-tier-fte/`
3. Check constitutional compliance in logs
4. Verify directory structure matches specification

## Bronze Tier Graduation Checklist

Use this checklist to verify Bronze Tier compliance:

- [ ] AI_Employee_Vault/ fully structured
- [ ] 3 skills exist in .claude/skills/ with valid SKILL.md
- [ ] main.py acts as orchestrator with continuous loop
- [ ] Logs generated for all actions
- [ ] Approval system blocks high-risk actions
- [ ] One workflow fully automated (email → draft reply)
- [ ] DRY_RUN mode respected
- [ ] Persistence loop continues until task in Done/
- [ ] All constitutional principles enforced
- [ ] Tests passing (>80% coverage)

## Appendix

### File Naming Conventions

- Tasks: `task-NNN.md` (e.g., task-001.md)
- Approvals: `approval-NNN.md` (e.g., approval-001.md)
- Logs: `YYYY-MM-DD.json` (e.g., 2026-02-16.json)

### Task File Template

```markdown
# Task: [Title]

**Type**: [task_type]
**Priority**: [LOW|MEDIUM|HIGH]
**Created**: [ISO 8601 timestamp]
**Status**: PENDING

## Context
[Task description and context]

## Expected Output
[What should be produced]
```

### Approval File Template

```markdown
# Approval Request: [Request ID]

**Task ID**: [task_id]
**Created**: [ISO 8601 timestamp]
**Risk Level**: [MEDIUM|HIGH]
**Action**: [action description]

## Justification
[Why needed]

## Impact
[What will happen]

## Approval
**Status**: PENDING
**Approver**: [leave blank]
**Decision**: [APPROVE|REJECT]
**Notes**: [optional]
```

---

**Congratulations!** You now have a working Bronze Tier Constitutional FTE. Start creating tasks and watch your autonomous assistant in action.
