# Bronze Tier Constitutional FTE

A Constitution-Compliant Digital Full-Time Employee (FTE) that implements autonomous task execution with safety guardrails, transparency, and human oversight.

## Overview

This Bronze Tier FTE demonstrates the Minimum Viable Constitutional FTE by implementing:

- **Local-First**: All data stored locally, no cloud dependencies
- **HITL Safety**: Human-in-the-Loop approval for high-risk actions
- **Proactivity**: Automatic task detection via file watchers
- **Persistence**: Ralph Wiggum persistence - tasks continue until complete
- **Transparency**: Complete audit logging of all actions
- **Cost Efficiency**: Minimal resource usage, efficient polling

## Features

### Core Capabilities

- **Autonomous Task Execution**: Processes tasks from `AI_Employee_Vault/Needs_Action/`
- **Risk-Based Approval**: Automatically evaluates task risk and blocks high-risk actions
- **Comprehensive Logging**: All actions logged to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Retry Logic**: Automatic retry with exponential backoff for failed tasks
- **File Watching**: Proactive monitoring for new files to create tasks automatically
- **Skill Management**: Dynamic skill loading and validation from `.claude/skills/`

### Constitutional Compliance

✅ **Local-First**: All operations use local file system
✅ **HITL Safety**: High-risk actions require manual approval
✅ **Transparency**: Every action logged with full context
✅ **Persistence**: Tasks retry up to 3 times before requesting help
✅ **Proactivity**: File watcher creates tasks automatically
✅ **Cost Efficiency**: 5-second polling interval, minimal resource usage

## Project Structure

```
AI-Employee-Hackathon/
├── AI_Employee_Vault/          # Operational workspace
│   ├── Business_Goals.md       # Business objectives
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Logs/                   # Daily audit logs (YYYY-MM-DD.json)
│   ├── Pending_Approval/       # High-risk tasks awaiting approval
│   ├── Briefings/              # Status briefings
│   ├── Done/                   # Completed tasks
│   └── Needs_Action/           # Tasks to be processed
│
├── .claude/skills/             # Structured skills
│   ├── task-orchestrator/      # Task execution coordination
│   ├── approval-guard/         # Risk evaluation and approval
│   └── logging-audit/          # Transparency and audit logging
│
├── src/                        # Source code
│   ├── models/                 # Pydantic data models
│   ├── skills/                 # Skill implementations
│   ├── orchestrator/           # Core orchestration logic
│   ├── watchers/               # Proactive monitoring
│   └── utils/                  # Utility functions
│
├── monitored/                  # Directory watched for new files
├── main.py                     # Orchestrator entry point
├── .env                        # Configuration (not committed)
└── .env.example                # Configuration template
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AI-Employee-Hackathon
   ```

2. Install dependencies:
   ```bash
   # Using pip
   pip install -e .

   # Using uv
   uv pip install -e .
   ```

3. Create configuration file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` to configure:
   ```env
   DRY_RUN=true          # Set to false for real execution
   LOG_LEVEL=INFO        # DEBUG, INFO, WARNING, ERROR
   POLL_INTERVAL=5       # Seconds between task checks
   MAX_RETRIES=3         # Maximum retry attempts
   ```

## Usage

### Starting the Orchestrator

```bash
python main.py
```

The orchestrator will:
1. Validate all skills in `.claude/skills/`
2. Recover any incomplete tasks from previous run
3. Start the file watcher on `monitored/` directory
4. Begin continuous polling loop (5-second interval)

### Creating Tasks

Tasks are markdown files in `AI_Employee_Vault/Needs_Action/` with this format:

```markdown
# Task Title

**Type**: draft_email
**Priority**: MEDIUM
**Created**: 2025-01-15T10:30:00
**Status**: PENDING

## Context
Description of what needs to be done.

## Expected Output
What the completed task should produce.
```

### Automatic Task Creation

Drop a `.txt` file in the `monitored/` directory and the file watcher will automatically create a task in `Needs_Action/`.

### Approving High-Risk Tasks

1. Check `AI_Employee_Vault/Pending_Approval/` for approval requests
2. Review the task details and justification
3. Edit the approval file:
   - Change `**Status**: PENDING` to `**Status**: APPROVED`
   - Or change to `**Status**: REJECTED` to deny
4. The orchestrator will detect the approval on next poll

## Skills

### Task Orchestrator
- **Purpose**: Coordinates multi-step task execution
- **Risk Level**: LOW to HIGH (depends on task type)
- **Location**: `.claude/skills/task-orchestrator/`

### Approval Guard
- **Purpose**: Evaluates risk and enforces HITL boundaries
- **Risk Level**: LOW
- **Location**: `.claude/skills/approval-guard/`

### Logging & Audit
- **Purpose**: Ensures transparency through comprehensive logging
- **Risk Level**: LOW
- **Location**: `.claude/skills/logging-audit/`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DRY_RUN` | `true` | Simulate actions without executing |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `POLL_INTERVAL` | `5` | Seconds between task checks |
| `MAX_RETRIES` | `3` | Maximum retry attempts for failed tasks |

### Risk Levels

- **LOW**: Auto-approved, executed immediately
- **MEDIUM**: Auto-approved with enhanced logging
- **HIGH**: Requires manual approval before execution

### High-Risk Actions

The following actions require approval:
- Payments over $100
- File deletions
- Email sending (non-draft)
- Social media posting
- Adding new payees
- Direct messages

## Logging

All actions are logged to `AI_Employee_Vault/Logs/YYYY-MM-DD.json` with:

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "action": "execute_task",
  "task_id": "task-001",
  "skill_used": "task-orchestrator",
  "risk_level": "LOW",
  "approval_status": "AUTO_APPROVED",
  "outcome": "SUCCESS",
  "duration_ms": 150
}
```

## Retry Logic

Failed tasks are automatically retried with exponential backoff:

1. **First retry**: Wait 5 seconds
2. **Second retry**: Wait 10 seconds
3. **Third retry**: Wait 20 seconds
4. **Max retries exceeded**: Create help request in `Needs_Action/`

## Troubleshooting

### Orchestrator won't start

- Check Python version: `python --version` (must be 3.11+)
- Verify dependencies: `pip list | grep -E "pydantic|watchdog"`
- Check `.env` file exists and is valid

### Tasks not processing

- Verify task file format matches template
- Check `Logs/` for error messages
- Ensure `DRY_RUN=false` for real execution
- Verify task status is `PENDING` not `IN_PROGRESS`

### Skills failing validation

- Check `.claude/skills/*/SKILL.md` files exist
- Verify all required sections are present
- Review logs for specific validation errors

### File watcher not detecting files

- Verify `monitored/` directory exists
- Check file extension matches pattern (default: `*.txt`)
- Review logs for watcher errors

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **Models** (`src/models/`): Pydantic schemas for data validation
- **Skills** (`src/skills/`): Skill implementations and loader
- **Orchestrator** (`src/orchestrator/`): Core task processing logic
- **Watchers** (`src/watchers/`): Proactive monitoring implementations
- **Utils** (`src/utils/`): Shared utility functions

### Adding New Skills

1. Create skill directory: `.claude/skills/my-skill/`
2. Create `SKILL.md` with all required sections
3. Implement skill class in `src/skills/my_skill.py`
4. Restart orchestrator to load new skill

## Bronze Tier Graduation Checklist

- [x] AI_Employee_Vault/ fully structured
- [x] 3 skills in .claude/skills/ with valid SKILL.md
- [x] main.py acts as orchestrator with continuous loop
- [x] Logs generated for all actions
- [x] Approval system blocks high-risk actions
- [x] One workflow fully automated (file watcher → draft reply)
- [x] DRY_RUN mode respected
- [x] Persistence loop continues until task in Done/
- [x] All constitutional principles enforced

## License

See LICENSE file for details.

## Contributing

This is a Bronze Tier Constitutional FTE implementation for the AI Employee Hackathon. Contributions should maintain constitutional compliance.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `AI_Employee_Vault/Logs/`
3. Verify constitutional compliance in `specs/001-bronze-tier-fte/`
