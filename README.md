# AI Employee - Silver Tier

**Autonomous Business Assistant with Multi-Channel Monitoring and Proactive Execution**

[![Status](https://img.shields.io/badge/status-Silver%20Tier-silver)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

A Constitution-Compliant Digital Full-Time Employee (FTE) that monitors multiple communication channels, generates structured execution plans, and takes external actions through secure MCP abstraction.

## Overview

Silver Tier upgrades Bronze from reactive automation to a proactive business assistant by adding:

### Core Constitutional Principles (Bronze Foundation)
- **Local-First**: All data stored locally, no cloud dependencies
- **HITL Safety**: Human-in-the-Loop approval for high-risk actions
- **Proactivity**: Autonomous monitoring and execution
- **Persistence**: Tasks continue until complete with retry logic
- **Transparency**: Complete audit logging of all actions
- **Cost Efficiency**: Efficient resource usage and scheduling

### Silver Tier Enhancements
- **Multi-Channel Monitoring**: Gmail, LinkedIn, WhatsApp watchers
- **Autonomous LinkedIn Posting**: Scheduled business content generation
- **Structured Reasoning**: Plan.md generation with step-by-step execution
- **MCP Integration**: Secure external action execution (email, social media)
- **Automated Scheduling**: OS-native scheduling (cron/Task Scheduler/launchd)
- **Skill-Based Architecture**: All AI logic in `.claude/skills/`

## Features

### Silver Tier Capabilities

#### Multi-Channel Monitoring
- **Gmail Watcher**: OAuth2-based email monitoring with automatic event creation
- **LinkedIn Watcher**: Selenium-based connection request and message detection
- **WhatsApp Watcher**: Message monitoring (optional)
- **Event Queue**: Atomic file-based queue with duplicate detection

#### Autonomous LinkedIn Posting
- Reads `Business_Goals.md` for business context
- Generates sales-oriented posts with hooks, CTAs, and hashtags
- Approval workflow before publishing
- Scheduled weekly posting
- Post analytics tracking

#### Structured Reasoning Loop
- Automatic Plan.md generation for complex tasks
- Step-by-step execution with progress tracking
- Retry logic with exponential backoff (5s, 15s, 45s)
- Error recovery and escalation
- State management through completion

#### MCP (Model Context Protocol) Integration
- **Email MCP Server**: Gmail API integration for sending emails
- **LinkedIn MCP Server**: Selenium-based post publishing
- JSON-RPC 2.0 protocol
- DRY_RUN mode support
- Comprehensive action logging

#### Human-in-the-Loop Approval
- Risk-based classification (low/medium/high)
- File-based approval workflow (drag-and-drop)
- 24-hour timeout with auto-reject
- Approval history tracking
- Constitutional compliance enforcement

#### Automated Scheduling
- OS-native scheduling support (cron/Task Scheduler/launchd)
- Configurable polling intervals
- Scheduled LinkedIn posts (weekly)
- Daily dashboard updates
- Health checks and monitoring

### Bronze Tier Foundation

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
│   ├── Business_Goals.md       # Business objectives and target audience
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Plan.md                 # Current execution plan (Silver)
│   ├── Logs/                   # Daily audit logs (YYYY-MM-DD.json)
│   ├── Pending_Approval/       # High-risk tasks awaiting approval
│   ├── Approved/               # Approved actions (Silver)
│   ├── Rejected/               # Rejected actions (Silver)
│   ├── Briefings/              # Status briefings
│   ├── Done/                   # Completed tasks
│   ├── Needs_Action/           # Tasks to be processed
│   └── Watchers/               # Event detection scripts (Silver)
│       ├── watcher_base.py     # Base watcher class
│       ├── gmail_watcher.py    # Gmail monitoring
│       ├── linkedin_watcher.py # LinkedIn monitoring
│       └── watcher_config.json # Watcher configuration
│
├── .claude/skills/             # Structured skills (AI logic)
│   ├── task-orchestrator/      # Event routing and coordination
│   ├── approval-guard/         # Risk evaluation and HITL
│   ├── logging-audit/          # Transparency and audit logging
│   ├── reasoning-loop/         # Plan generation and execution (Silver)
│   ├── email-mcp-sender/       # Email actions via MCP (Silver)
│   └── linkedin-post-generator/ # LinkedIn automation (Silver)
│
├── mcp_servers/                # MCP abstraction layer (Silver)
│   ├── mcp_base.py             # JSON-RPC 2.0 base server
│   ├── email_server.py         # Gmail API MCP server
│   ├── linkedin_server.py      # LinkedIn Selenium MCP server
│   └── server_config.json      # MCP server configuration
│
├── scripts/                    # Utility and coordination scripts
│   ├── orchestrator.py         # Main coordination loop (Silver)
│   ├── watchdog.py             # System health monitoring (Silver)
│   ├── update_dashboard.py     # Dashboard updates (Silver)
│   ├── logger.py               # JSON logging system
│   ├── event_queue.py          # Event queue management
│   ├── approval_workflow.py    # Approval system (Silver)
│   ├── plan_generator.py       # Plan.md generation (Silver)
│   ├── step_executor.py        # Step execution with retry (Silver)
│   ├── task_analyzer.py        # Event classification (Silver)
│   ├── risk_classifier.py      # Risk assessment
│   ├── mcp_client.py           # MCP client wrapper (Silver)
│   ├── business_goals_reader.py # Business context (Silver)
│   ├── post_generator.py       # LinkedIn post generation (Silver)
│   ├── linkedin_scheduler.py   # Scheduled posting (Silver)
│   ├── run_watchers.py         # Watcher execution (Silver)
│   ├── scheduler_setup.sh      # Linux/macOS cron setup (Silver)
│   ├── setup_windows_scheduler.ps1 # Windows Task Scheduler (Silver)
│   ├── setup_macos_scheduler.sh # macOS launchd setup (Silver)
│   └── validate_scheduler.py   # Scheduler validation (Silver)
│
├── src/                        # Source code (Bronze foundation)
│   ├── models/                 # Pydantic data models
│   ├── skills/                 # Skill implementations
│   ├── orchestrator/           # Core orchestration logic
│   ├── watchers/               # Proactive monitoring
│   └── utils/                  # Utility functions
│
├── specs/                      # Feature specifications
│   ├── 001-silver-tier-upgrade/ # Silver Tier spec, plan, tasks
│   └── ...
│
├── monitored/                  # Directory watched for new files (Bronze)
├── main.py                     # Bronze orchestrator entry point
├── requirements.txt            # Python dependencies
├── .env                        # Configuration (not committed)
└── .env.example                # Configuration template
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Gmail API credentials (for email watcher)
- LinkedIn account (for LinkedIn automation)
- Chrome/Chromium browser (for LinkedIn Selenium automation)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-Employee-Hackathon
   ```

2. **Install dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt

   # Using uv
   uv pip install -e .
   ```

3. **Create configuration file**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Configure Gmail OAuth2** (for email watcher):
   ```bash
   # Place your Gmail API credentials in gmail_credentials.json
   # First run will open browser for OAuth2 consent
   python AI_Employee_Vault/Watchers/gmail_watcher.py --test
   ```

5. **Configure Business Goals**:
   ```bash
   # Edit AI_Employee_Vault/Business_Goals.md with your objectives
   nano AI_Employee_Vault/Business_Goals.md
   ```

6. **Set up watchers**:
   ```bash
   # Edit watcher configuration
   nano AI_Employee_Vault/Watchers/watcher_config.json
   ```

## Usage

### Running the System

#### Silver Tier Orchestrator (Recommended)

**Test Mode (DRY_RUN)**:
```bash
# Run once in test mode (no real actions)
DRY_RUN=true python scripts/orchestrator.py --once

# Run continuously in test mode (5-minute cycles)
DRY_RUN=true python scripts/orchestrator.py --interval 300
```

**Production Mode**:
```bash
# Run once (for cron/scheduler)
DRY_RUN=false python scripts/orchestrator.py --once

# Run continuously
DRY_RUN=false python scripts/orchestrator.py --interval 300
```

#### Bronze Tier Orchestrator (Legacy)

```bash
python main.py
```

The Bronze orchestrator will:
1. Validate all skills in `.claude/skills/`
2. Recover any incomplete tasks from previous run
3. Start the file watcher on `monitored/` directory
4. Begin continuous polling loop (5-second interval)

### Setting Up Automated Scheduling

#### Linux/macOS (cron)
```bash
bash scripts/scheduler_setup.sh
```

This creates cron jobs for:
- Watchers: Every 5 minutes
- Orchestrator: Every 10 minutes
- LinkedIn posts: Weekly (Monday 9 AM)
- Dashboard updates: Daily (8 AM)

#### macOS (launchd)
```bash
bash scripts/setup_macos_scheduler.sh
```

Creates launchd agents for automated execution.

#### Windows (Task Scheduler)
```powershell
# Run as Administrator
.\scripts\setup_windows_scheduler.ps1
```

Creates scheduled tasks for all components.

#### Validate Scheduler Setup
```bash
python scripts/validate_scheduler.py
```

### Running Individual Components

#### Test Watchers
```bash
# Gmail watcher
python AI_Employee_Vault/Watchers/gmail_watcher.py --test

# LinkedIn watcher
python AI_Employee_Vault/Watchers/linkedin_watcher.py --test

# Run all watchers once
python scripts/run_watchers.py --once
```

#### Test MCP Servers
```bash
# Email MCP server
python mcp_servers/email_server.py --test

# LinkedIn MCP server
python mcp_servers/linkedin_server.py --test
```

#### System Health Check
```bash
python scripts/watchdog.py
```

#### Update Dashboard
```bash
python scripts/update_dashboard.py
```

### Creating Tasks

#### Manual Task Creation

Tasks are markdown files in `AI_Employee_Vault/Needs_Action/` with this format:

```markdown
# Task Title

**Type**: draft_email
**Priority**: MEDIUM
**Created**: 2026-02-18T10:30:00
**Status**: PENDING

## Context
Description of what needs to be done.

## Expected Output
What the completed task should produce.
```

#### Automatic Task Creation (Bronze)

Drop a `.txt` file in the `monitored/` directory and the file watcher will automatically create a task in `Needs_Action/`.

#### Event-Based Task Creation (Silver)

Watchers automatically create tasks when they detect:
- **Gmail**: New emails in inbox
- **LinkedIn**: Connection requests, messages
- **WhatsApp**: New messages (if enabled)

Events are normalized to JSON format and placed in `Needs_Action/`.

### Approval Workflow

#### How It Works

1. **Risk Classification**: Actions are classified as low/medium/high risk
2. **Approval Request**: Medium/high risk actions create approval files in `Pending_Approval/`
3. **Human Decision**: Drag file to `Approved/` or `Rejected/`
4. **Execution**: System detects approval and proceeds
5. **Timeout**: Auto-reject after 24 hours if no decision

#### Risk Levels

- **Low**: Frequent contacts, routine tasks → Auto-execute
- **Medium**: New contacts, public posts → Require approval
- **High**: Payments, deletions, new vendors → Require approval

#### Approval File Format

```markdown
# Approval Request: Email to New Contact

**Action ID**: email_20260218_001
**Risk Level**: MEDIUM
**Created**: 2026-02-18 10:30:00

## Action Details
- **Type**: Email Send
- **To**: potential.client@example.com
- **Subject**: Re: Question about your services

## Content Preview
Hi, thank you for your interest...

## Risk Assessment
- New contact (no previous communication)
- Business inquiry (sales opportunity)

## Decision
Move this file to:
- `Approved/` to proceed
- `Rejected/` to cancel
```

#### Approving Tasks

**Method 1: File Manager (Recommended)**
1. Open `AI_Employee_Vault/Pending_Approval/` in file manager
2. Review the approval request file
3. Drag file to `Approved/` or `Rejected/` folder

**Method 2: Command Line**
```bash
# Approve
mv AI_Employee_Vault/Pending_Approval/email_20260218_001.md AI_Employee_Vault/Approved/

# Reject
mv AI_Employee_Vault/Pending_Approval/email_20260218_001.md AI_Employee_Vault/Rejected/
```

**Method 3: Edit Status (Legacy)**
1. Open approval file in text editor
2. Change `**Status**: PENDING` to `**Status**: APPROVED` or `**Status**: REJECTED`
3. Save file

## Skills

### Silver Tier Skills

#### Task Orchestrator
- **Purpose**: Coordinates event routing and multi-step task execution
- **Responsibilities**:
  - Route events to appropriate skills
  - Manage workflow state transitions
  - Handle concurrency and resource limits
  - Coordinate approval workflows
- **Risk Level**: LOW (coordination only)
- **Location**: `.claude/skills/task-orchestrator/`

#### Approval Guard
- **Purpose**: Evaluates risk and enforces HITL boundaries
- **Responsibilities**:
  - Classify action risk (low/medium/high)
  - Create approval requests for risky actions
  - Monitor approval status
  - Enforce timeout policies
- **Risk Level**: LOW (safety mechanism)
- **Location**: `.claude/skills/approval-guard/`

#### Logging & Audit
- **Purpose**: Ensures transparency through comprehensive logging
- **Responsibilities**:
  - Log all actions with full metadata
  - Track performance metrics
  - Flag constitutional violations
  - Generate audit reports
- **Risk Level**: LOW (read-only logging)
- **Location**: `.claude/skills/logging-audit/`

#### Reasoning Loop
- **Purpose**: Generates and executes structured plans for complex tasks
- **Responsibilities**:
  - Analyze event complexity
  - Generate Plan.md with steps
  - Execute steps sequentially
  - Handle errors and retries
  - Update plan status
- **Risk Level**: MEDIUM (executes multi-step workflows)
- **Location**: `.claude/skills/reasoning-loop/`

#### Email MCP Sender
- **Purpose**: Sends emails through MCP abstraction
- **Responsibilities**:
  - Send emails via Gmail API
  - Validate email addresses
  - Check delivery status
  - Respect DRY_RUN mode
- **Risk Level**: MEDIUM to HIGH (external communication)
- **Location**: `.claude/skills/email-mcp-sender/`

#### LinkedIn Post Generator
- **Purpose**: Generates and publishes LinkedIn business content
- **Responsibilities**:
  - Read Business_Goals.md
  - Generate sales-oriented posts
  - Create drafts for approval
  - Publish via MCP
  - Track post analytics
- **Risk Level**: MEDIUM (public posting)
- **Location**: `.claude/skills/linkedin-post-generator/`

## Configuration

### Environment Variables

#### Core Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `DRY_RUN` | `true` | Simulate actions without executing |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

#### Bronze Settings (Legacy)
| Variable | Default | Description |
|----------|---------|-------------|
| `POLL_INTERVAL` | `5` | Seconds between task checks (Bronze orchestrator) |
| `MAX_RETRIES` | `3` | Maximum retry attempts for failed tasks |

#### Silver Tier Settings

**Watcher Configuration**:
| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_CREDENTIALS_FILE` | `gmail_credentials.json` | Gmail API credentials path |
| `GMAIL_TOKEN_FILE` | `gmail_token.json` | Gmail OAuth2 token storage |
| `GMAIL_POLL_INTERVAL` | `300` | Gmail polling interval (seconds) |
| `LINKEDIN_EMAIL` | - | LinkedIn account email |
| `LINKEDIN_PASSWORD` | - | LinkedIn account password |
| `LINKEDIN_POLL_INTERVAL` | `900` | LinkedIn polling interval (seconds) |
| `WHATSAPP_POLL_INTERVAL` | `600` | WhatsApp polling interval (seconds) |

**MCP Server Configuration**:
| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_EMAIL_PORT` | `5001` | Email MCP server port |
| `MCP_LINKEDIN_PORT` | `5002` | LinkedIn MCP server port |

**Orchestrator Configuration**:
| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_CYCLE_INTERVAL` | `300` | Seconds between orchestrator cycles |
| `APPROVAL_TIMEOUT_HOURS` | `24` | Auto-reject approvals after N hours |
| `LINKEDIN_POST_SCHEDULE` | `weekly` | LinkedIn posting frequency |
| `DASHBOARD_UPDATE_SCHEDULE` | `daily` | Dashboard update frequency |

### Watcher Configuration File

Edit `AI_Employee_Vault/Watchers/watcher_config.json`:

```json
{
  "gmail": {
    "enabled": true,
    "poll_interval": 300,
    "labels": ["INBOX"]
  },
  "linkedin": {
    "enabled": true,
    "poll_interval": 900,
    "headless": true
  },
  "whatsapp": {
    "enabled": false,
    "poll_interval": 600
  }
}
```

### MCP Server Configuration

Edit `mcp_servers/server_config.json`:

```json
{
  "email": {
    "port": 5001,
    "host": "localhost",
    "timeout": 30
  },
  "linkedin": {
    "port": 5002,
    "host": "localhost",
    "timeout": 60,
    "headless": true
  }
}
```

### Risk Levels

- **LOW**: Auto-approved, executed immediately
  - Frequent contacts (email history exists)
  - Routine tasks (dashboard updates, health checks)
  - Read-only operations

- **MEDIUM**: Requires approval with enhanced logging
  - New contacts (no previous communication)
  - Public social media posts
  - Non-routine external communications

- **HIGH**: Requires manual approval before execution
  - Payments over $100
  - File deletions (irreversible)
  - New vendor/payee additions
  - Direct messages to unknown recipients
  - Any action with financial impact

### High-Risk Actions

The following actions always require approval:
- **Financial**: Payments, refunds, new payees
- **Destructive**: File deletions, account closures
- **Public**: Social media posts, public comments
- **Communication**: Emails to new contacts, direct messages
- **Administrative**: User account changes, permission modifications

## Logging

### Log Format

All actions are logged to `AI_Employee_Vault/Logs/YYYY-MM-DD.json` in JSON format:

```json
{
  "timestamp": "2026-02-18T10:30:00Z",
  "component": "orchestrator",
  "action": "event_routed",
  "actor": "task-orchestrator",
  "target": "gmail_20260218_001",
  "status": "success",
  "details": {
    "duration_ms": 150,
    "routed_to": "reasoning-loop",
    "complexity": "complex",
    "category": "sales"
  }
}
```

### Log Components

- **timestamp**: ISO 8601 format with Z suffix
- **component**: System component (orchestrator, watcher, reasoning, mcp, approval)
- **action**: Specific action taken (event_detected, plan_created, email_sent, etc.)
- **actor**: Skill or system component performing action
- **target**: Event ID or resource being acted upon
- **status**: success, warning, or error
- **details**: Additional context (duration, retry count, metadata)

### Viewing Logs

```bash
# View today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq .

# Search for errors
grep '"status":"error"' AI_Employee_Vault/Logs/*.json

# View specific event
grep '"target":"gmail_20260218_001"' AI_Employee_Vault/Logs/*.json | jq .

# Count events by component
jq -r '.component' AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | sort | uniq -c
```

### Log Rotation

Logs older than 90 days are automatically archived:

```bash
# Manual log rotation
python scripts/archive_logs.py

# Logs are moved to AI_Employee_Vault/Logs/archive/
```

## Monitoring

### Dashboard

View real-time system status:

```bash
cat AI_Employee_Vault/Dashboard.md
```

Dashboard includes:
- System status (running/stopped)
- Active tasks count
- Pending approvals count
- Recent events (last 10)
- Watcher status
- Error summary
- Last update timestamp

### Health Check

Run comprehensive health check:

```bash
python scripts/watchdog.py
```

Checks:
- **Watchers**: Are they running? Last execution time?
- **Event Queue**: Queue depth, stale events
- **Approvals**: Pending count, timeouts
- **Logs**: File health, recent errors
- **Disk Space**: Available storage
- **Stale Tasks**: Tasks stuck in progress

### System Metrics

```bash
# View performance metrics
python scripts/health_check.py --metrics

# Generate weekly report
python scripts/generate_weekly_report.py
```

## Retry Logic

Failed tasks are automatically retried with exponential backoff:

1. **First retry**: Wait 5 seconds
2. **Second retry**: Wait 15 seconds
3. **Third retry**: Wait 45 seconds
4. **Max retries exceeded**: Create escalation task in `Needs_Action/`

### Retry Behavior

- **Transient Errors**: Network timeouts, file locks, temporary unavailability → Retry
- **Permanent Errors**: Invalid format, missing data, authentication failures → No retry, escalate immediately
- **Retry Tracking**: All attempts logged with duration and error details
- **Escalation**: Failed tasks create `ESCALATION_*.md` files for human review

## Troubleshooting

### Orchestrator Issues

**Orchestrator won't start**:
- Check Python version: `python --version` (must be 3.11+)
- Verify dependencies: `pip list | grep -E "pydantic|watchdog|selenium"`
- Check `.env` file exists and is valid
- Review logs: `cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.status=="error")'`

**Tasks not processing**:
- Verify task file format matches template
- Check `Logs/` for error messages
- Ensure `DRY_RUN=false` for real execution
- Verify task status is `PENDING` not `IN_PROGRESS`
- Check event queue: `ls AI_Employee_Vault/Needs_Action/`

### Watcher Issues

**Gmail watcher not detecting emails**:
- Verify OAuth2 token: `ls gmail_token.json`
- Re-authenticate: `python AI_Employee_Vault/Watchers/gmail_watcher.py --test`
- Check credentials: Ensure `gmail_credentials.json` is valid
- Review watcher logs for authentication errors

**LinkedIn watcher failing**:
- Verify Chrome/Chromium installed: `which chromium` or `which google-chrome`
- Check LinkedIn credentials in `.env`
- Try non-headless mode: Set `headless: false` in `watcher_config.json`
- Check for CAPTCHA or login challenges

**Watchers not running automatically**:
- Verify scheduler setup: `python scripts/validate_scheduler.py`
- Check cron jobs: `crontab -l` (Linux/macOS)
- Check Task Scheduler: `Get-ScheduledTask | Where-Object {$_.TaskName -like 'AI_Employee*'}` (Windows)
- Review scheduler logs

### Approval Issues

**Approvals not being detected**:
- Verify file moved to correct directory (`Approved/` or `Rejected/`)
- Check file permissions: `ls -la AI_Employee_Vault/Approved/`
- Ensure orchestrator is running
- Check approval timeout (default 24 hours)

**Approval timeout too short/long**:
- Edit `.env`: `APPROVAL_TIMEOUT_HOURS=48` (for 48 hours)
- Restart orchestrator

### MCP Server Issues

**Email MCP server not sending**:
- Verify Gmail API credentials
- Check MCP server is running: `ps aux | grep email_server`
- Test MCP server: `python mcp_servers/email_server.py --test`
- Review MCP logs for errors

**LinkedIn MCP server failing**:
- Verify Selenium WebDriver installed
- Check Chrome/Chromium version compatibility
- Test MCP server: `python mcp_servers/linkedin_server.py --test`
- Try non-headless mode for debugging

### Skills Issues

**Skills failing validation**:
- Check `.claude/skills/*/SKILL.md` files exist
- Verify all required sections are present (Purpose, Responsibilities, Examples)
- Review logs for specific validation errors
- Ensure skill directory structure is correct

**Skill not being invoked**:
- Check orchestrator routing logic in `scripts/orchestrator.py`
- Verify event type matches routing rules
- Review logs for routing decisions
- Check skill is enabled in configuration

### File System Issues

**File watcher not detecting files** (Bronze):
- Verify `monitored/` directory exists
- Check file extension matches pattern (default: `*.txt`)
- Review logs for watcher errors
- Ensure file permissions allow reading

**Disk space issues**:
- Check available space: `df -h`
- Run log rotation: `python scripts/archive_logs.py`
- Clean up old tasks: `find AI_Employee_Vault/Done/ -mtime +90 -delete`

### Performance Issues

**Slow event processing**:
- Check concurrent task limit (default: 10)
- Review system resources: `top` or `htop`
- Check for stale tasks: `python scripts/watchdog.py`
- Optimize polling intervals in `.env`

**High memory usage**:
- Check for memory leaks in logs
- Restart orchestrator periodically
- Reduce concurrent task limit
- Archive old logs and tasks

## Development

### Running Tests

```bash
# Test all components
pytest tests/

# Test specific components
python AI_Employee_Vault/Watchers/gmail_watcher.py --test
python AI_Employee_Vault/Watchers/linkedin_watcher.py --test
python mcp_servers/email_server.py --test
python mcp_servers/linkedin_server.py --test
python scripts/orchestrator.py --once --dry-run

# Validate scheduler setup
python scripts/validate_scheduler.py

# Run health check
python scripts/watchdog.py
```

### Code Structure

#### Bronze Foundation
- **Models** (`src/models/`): Pydantic schemas for data validation
- **Skills** (`src/skills/`): Skill implementations and loader
- **Orchestrator** (`src/orchestrator/`): Core task processing logic
- **Watchers** (`src/watchers/`): Proactive monitoring implementations
- **Utils** (`src/utils/`): Shared utility functions

#### Silver Tier Components
- **Watchers** (`AI_Employee_Vault/Watchers/`): Event detection scripts
- **MCP Servers** (`mcp_servers/`): External action abstraction
- **Scripts** (`scripts/`): Coordination and utility scripts
- **Skills** (`.claude/skills/`): AI reasoning and decision logic

### Adding New Skills

1. **Create skill directory**:
   ```bash
   mkdir -p .claude/skills/my-skill
   ```

2. **Create required files**:
   - `SKILL.md`: Skill documentation with Purpose, Responsibilities, Examples
   - `prompt.txt`: Skill prompt defining role and behavior
   - `examples.md`: Usage examples and test cases

3. **Update orchestrator routing**:
   - Edit `scripts/orchestrator.py`
   - Add routing logic in `_route_to_skill()` method

4. **Test the skill**:
   ```bash
   # Create test event
   # Verify skill is invoked
   # Check logs for skill execution
   ```

### Adding New Watchers

1. **Create watcher class** inheriting from `WatcherBase`:
   ```python
   from AI_Employee_Vault.Watchers.watcher_base import WatcherBase

   class MyWatcher(WatcherBase):
       def poll_once(self):
           # Detection logic
           pass
   ```

2. **Add configuration** to `watcher_config.json`

3. **Register watcher** in `scripts/run_watchers.py`

4. **Test the watcher**:
   ```bash
   python AI_Employee_Vault/Watchers/my_watcher.py --test
   ```

### Adding New MCP Servers

1. **Create server class** inheriting from `MCPServer`:
   ```python
   from mcp_servers.mcp_base import MCPServer

   class MyMCPServer(MCPServer):
       def handle_request(self, method, params):
           # Implementation
           pass
   ```

2. **Add configuration** to `server_config.json`

3. **Create corresponding skill** in `.claude/skills/`

4. **Test the server**:
   ```bash
   python mcp_servers/my_server.py --test
   ```

## Silver Tier Graduation Checklist

### Bronze Foundation (Complete ✅)
- [x] AI_Employee_Vault/ fully structured
- [x] 3 skills in .claude/skills/ with valid SKILL.md
- [x] main.py acts as orchestrator with continuous loop
- [x] Logs generated for all actions
- [x] Approval system blocks high-risk actions
- [x] One workflow fully automated (file watcher → draft reply)
- [x] DRY_RUN mode respected
- [x] Persistence loop continues until task in Done/
- [x] All constitutional principles enforced

### Silver Tier Requirements (Complete ✅)
- [x] 2+ watchers operational (Gmail, LinkedIn)
- [x] LinkedIn auto-posting with approval workflow
- [x] Plan.md generation and execution (reasoning-loop skill)
- [x] 1+ working MCP server (email, LinkedIn)
- [x] HITL workflow enforced for medium/high risk actions
- [x] Automated scheduling (cron/Task Scheduler/launchd)
- [x] All AI logic in .claude/skills/ (6 skills total)
- [x] Event-based task creation
- [x] Multi-step workflow coordination
- [x] Constitutional compliance validated

### Verification
- [x] All skills have SKILL.md, prompt.txt, examples.md
- [x] Watchers detect events and create tasks
- [x] Orchestrator routes events to appropriate skills
- [x] Approval workflow blocks risky actions
- [x] MCP abstraction for all external actions
- [x] Comprehensive logging and audit trail
- [x] Scheduler setup scripts for all platforms
- [x] Health monitoring and validation tools

## Performance Metrics

- **Watcher Polling**: 5-15 minutes (configurable)
- **Event Processing**: < 30 seconds per event
- **Concurrent Tasks**: Max 10 simultaneous
- **Log Retention**: 90 days (with automatic rotation)
- **Approval Timeout**: 24 hours (configurable)
- **Retry Attempts**: 3 with exponential backoff (5s, 15s, 45s)

## Security

- **Credentials**: All secrets in `.env` (never in code)
- **OAuth2**: Gmail uses OAuth2 (no password storage)
- **File Permissions**: Restricted access to sensitive files
- **DRY_RUN**: Test mode prevents real actions
- **Audit Trail**: Complete logging for accountability
- **MCP Abstraction**: No direct API calls in business logic
- **Approval Workflow**: Human oversight for risky actions

## Roadmap

### ✅ Bronze Tier (Complete)
- Constitutional compliance
- File-based task execution
- Approval workflow
- Comprehensive logging
- Skill-based architecture

### ✅ Silver Tier (Complete)
- Multi-channel monitoring (Gmail, LinkedIn)
- LinkedIn automation
- Reasoning loops with Plan.md
- MCP integration
- HITL workflows
- Automated scheduling

### 🚧 Gold Tier (Future)
- Advanced NLP for intent detection
- Multi-step conversation handling
- CRM integration (Salesforce, HubSpot)
- Analytics dashboard with visualizations
- Mobile notifications (push, SMS)
- Team collaboration features
- Voice interface integration
- Advanced workflow automation
- Machine learning for optimization

## License

MIT License - See LICENSE file for details.

## Contributing

See CONTRIBUTING.md for development guidelines, code standards, and contribution process.

This is a Silver Tier Constitutional FTE implementation for the AI Employee Hackathon. All contributions must maintain constitutional compliance.

## Support

### Documentation
- **Specifications**: `specs/001-silver-tier-upgrade/`
- **Skills**: `.claude/skills/*/SKILL.md`
- **Verification**: `VERIFICATION_REPORT.md`

### Troubleshooting
- **Issues**: Check `AI_Employee_Vault/Needs_Action/ESCALATION_*.md`
- **Logs**: `AI_Employee_Vault/Logs/`
- **Health**: Run `python scripts/watchdog.py`
- **Dashboard**: View `AI_Employee_Vault/Dashboard.md`

### Getting Help
1. Check the troubleshooting section above
2. Review logs in `AI_Employee_Vault/Logs/`
3. Run health check: `python scripts/watchdog.py`
4. Validate scheduler: `python scripts/validate_scheduler.py`
5. Check constitutional compliance in specs

---

**Status**: Silver Tier Complete ✅
**Last Updated**: 2026-02-18
**Python**: 3.11+
**Platform**: Linux, macOS, Windows
