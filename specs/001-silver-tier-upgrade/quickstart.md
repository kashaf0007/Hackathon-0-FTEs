# Quickstart Guide: Silver Tier Setup

**Feature**: Silver Tier - Functional Business Assistant
**Date**: 2026-02-17
**Version**: 1.0.0

## Overview

This guide walks you through setting up and testing the Silver Tier system from scratch. Follow these steps in order to get your Digital FTE operational.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher (for WhatsApp watcher)
- **Git**: For version control
- **Chrome/Chromium**: For LinkedIn automation
- **Disk Space**: 2GB minimum for logs and data

### Required Accounts

- Gmail account with API access enabled
- LinkedIn account
- WhatsApp account (optional, for WhatsApp watcher)

### Knowledge Prerequisites

- Basic command line usage
- Understanding of environment variables
- Familiarity with JSON and Markdown formats

---

## Installation Steps

### Step 1: Clone and Setup Repository

```bash
# Navigate to project directory
cd AI-Employee-Hackathon

# Verify you're on the correct branch
git branch --show-current
# Should show: 001-silver-tier-upgrade

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Create Directory Structure

```bash
# Create AI Employee Vault directories
mkdir -p AI_Employee_Vault/{Logs,Pending_Approval,Approved,Rejected,Briefings,Done,Needs_Action,Watchers}

# Create MCP servers directory
mkdir -p mcp_servers

# Create scripts directory
mkdir -p scripts

# Create tests directory
mkdir -p tests/{unit,integration,fixtures}

# Create .claude/skills directory
mkdir -p .claude/skills/{task-orchestrator,approval-guard,logging-audit,linkedin-post-generator,email-mcp-sender,reasoning-loop}
```

### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required .env Configuration**:

```bash
# System Configuration
DRY_RUN=true  # Set to false for production
LOG_LEVEL=info

# Gmail Configuration
EMAIL_PROVIDER=gmail
EMAIL_FROM=your-email@gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Use App Password, not regular password

# LinkedIn Configuration
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password
LINKEDIN_API_MODE=selenium  # or 'api' if you have API access

# WhatsApp Configuration (optional)
WHATSAPP_ENABLED=false  # Set to true to enable WhatsApp watcher
WHATSAPP_SESSION_PATH=.wwebjs_auth

# MCP Server Configuration
MCP_EMAIL_PORT=5000
MCP_LINKEDIN_PORT=5001

# Scheduling Configuration
WATCHER_INTERVAL_MINUTES=10
REASONING_LOOP_INTERVAL_MINUTES=10
LINKEDIN_POST_DAY=sunday
LINKEDIN_POST_HOUR=9
DASHBOARD_UPDATE_HOUR=8

# Approval Configuration
APPROVAL_TIMEOUT_HOURS=24
```

### Step 4: Setup Gmail API

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create a new project: "AI Employee"
   - Enable Gmail API for the project

2. **Create OAuth2 Credentials**:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "AI Employee Gmail Watcher"
   - Download credentials JSON

3. **Save Credentials**:
   ```bash
   # Save downloaded file as:
   mv ~/Downloads/client_secret_*.json AI_Employee_Vault/Watchers/gmail_credentials.json

   # Add to .gitignore
   echo "AI_Employee_Vault/Watchers/gmail_credentials.json" >> .gitignore
   echo "AI_Employee_Vault/Watchers/gmail_token.json" >> .gitignore
   ```

4. **Authenticate**:
   ```bash
   # Run authentication flow (one-time)
   python AI_Employee_Vault/Watchers/gmail_watcher.py --authenticate

   # This will open a browser window for OAuth consent
   # Grant permissions and close the browser
   # Token will be saved to gmail_token.json
   ```

### Step 5: Setup LinkedIn Automation

1. **Install ChromeDriver**:
   ```bash
   # On macOS:
   brew install chromedriver

   # On Ubuntu:
   sudo apt-get install chromium-chromedriver

   # On Windows:
   # Download from https://chromedriver.chromium.org/
   # Add to PATH
   ```

2. **Test LinkedIn Login**:
   ```bash
   # Test LinkedIn credentials (dry run)
   python mcp_servers/linkedin_server.py --test-login

   # This will open a browser and attempt to log in
   # Verify it works, then close the browser
   ```

### Step 6: Setup WhatsApp (Optional)

1. **Install Node.js Dependencies**:
   ```bash
   cd AI_Employee_Vault/Watchers
   npm install whatsapp-web.js qrcode-terminal
   ```

2. **Start WhatsApp Bridge**:
   ```bash
   # Start the Node.js bridge server
   node whatsapp_bridge.js

   # Scan QR code with WhatsApp mobile app
   # Session will be saved to .wwebjs_auth/
   ```

3. **Add to .gitignore**:
   ```bash
   echo ".wwebjs_auth/" >> .gitignore
   ```

### Step 7: Create Business Goals

```bash
# Create Business_Goals.md template
cat > AI_Employee_Vault/Business_Goals.md << 'EOF'
# Business Goals

**Last Updated**: 2026-02-17
**Version**: 1.0.0

## Target Audience

[Describe your ideal customers/clients]

## Key Messages

1. [Your key message 1]
2. [Your key message 2]
3. [Your key message 3]

## Value Proposition

[What makes your business unique]

## Content Guidelines

### Tone
- Professional yet approachable
- Data-driven and results-oriented
- Helpful and educational

### Topics to Emphasize
- AI automation and efficiency
- Business process optimization
- Cost savings and ROI

### Topics to Avoid
- Controversial political topics
- Unverified claims
- Competitor criticism

## Success Metrics

- Engagement rate: > 5%
- Connection requests: > 10 per week
- Inbound inquiries: > 2 per month

## Call-to-Action

"Interested in learning more? Let's connect and discuss how automation can transform your business."

## Brand Voice

Professional, knowledgeable, and results-focused. We speak with authority on AI and automation while remaining accessible to non-technical audiences.
EOF
```

---

## Testing Procedures

### Test 1: Event Detection (Watchers)

**Objective**: Verify watchers can detect events and create task files

```bash
# Test Gmail watcher
python AI_Employee_Vault/Watchers/gmail_watcher.py --test

# Expected output:
# - Connects to Gmail API
# - Checks for new emails
# - Creates event file in Needs_Action/ if new email found
# - Logs activity to Logs/YYYY-MM-DD.json

# Verify event file was created
ls -la AI_Employee_Vault/Needs_Action/

# Inspect event file
cat AI_Employee_Vault/Needs_Action/20260217_*.json
```

**Success Criteria**:
- ✅ Watcher runs without errors
- ✅ Event file created in Needs_Action/
- ✅ Event file matches schema (event-schema.json)
- ✅ Log entry created in Logs/

### Test 2: Risk Classification

**Objective**: Verify risk classifier correctly categorizes actions

```bash
# Run risk classification tests
pytest tests/unit/test_risk_classification.py -v

# Test cases:
# - High risk: payment > $500
# - High risk: new payee
# - Medium risk: email to new contact
# - Medium risk: LinkedIn post
# - Low risk: email to known contact
```

**Success Criteria**:
- ✅ All test cases pass
- ✅ Risk levels assigned correctly
- ✅ Risk reasons are clear and actionable

### Test 3: Approval Workflow

**Objective**: Verify HITL approval workflow functions correctly

```bash
# Run approval workflow test
pytest tests/integration/test_approval_workflow.py -v

# This test will:
# 1. Create approval request in Pending_Approval/
# 2. Simulate human approval (move file to Approved/)
# 3. Verify action executes
# 4. Verify task moves to Done/
```

**Success Criteria**:
- ✅ Approval file created with correct format
- ✅ System waits for approval (doesn't execute immediately)
- ✅ Action executes after approval
- ✅ All steps logged

### Test 4: MCP Server Integration

**Objective**: Verify MCP servers can execute actions

```bash
# Test email MCP server (dry run)
python mcp_servers/email_server.py --test

# Expected output:
# - Server starts successfully
# - Test email simulated (DRY_RUN=true)
# - Response includes message_id and status
# - Action logged

# Test LinkedIn MCP server (dry run)
python mcp_servers/linkedin_server.py --test

# Expected output:
# - Server starts successfully
# - Test post simulated (DRY_RUN=true)
# - Response includes post_id and status
# - Action logged
```

**Success Criteria**:
- ✅ MCP servers start without errors
- ✅ Test actions simulated successfully
- ✅ Responses match contract schema
- ✅ All actions logged

### Test 5: LinkedIn Post Generation

**Objective**: Verify LinkedIn post generator creates appropriate content

```bash
# Test LinkedIn post generator skill
python -c "
from claude_skills import linkedin_post_generator
post = linkedin_post_generator.generate_post('AI_Employee_Vault/Business_Goals.md')
print(post)
"

# Expected output:
# - Post content aligned with Business_Goals.md
# - Appropriate hashtags included
# - Call-to-action present
# - Length within LinkedIn limits (< 3000 chars)
```

**Success Criteria**:
- ✅ Post generated successfully
- ✅ Content aligns with business goals
- ✅ Professional tone maintained
- ✅ Hashtags relevant and appropriate

### Test 6: Reasoning Loop

**Objective**: Verify reasoning loop generates and executes plans

```bash
# Create test event
cat > AI_Employee_Vault/Needs_Action/test_event.json << 'EOF'
{
  "event_id": "20260217_120000_test_001",
  "source": "gmail",
  "type": "new_email",
  "timestamp": "2026-02-17T12:00:00Z",
  "priority": "medium",
  "content": {
    "subject": "Interested in your services",
    "body": "Hi, I'd like to learn more about your AI consulting services.",
    "from": "prospect@example.com",
    "to": "me@example.com"
  },
  "metadata": {
    "contact_history": "new"
  },
  "created_at": "2026-02-17T12:00:05Z",
  "processed": false
}
EOF

# Run reasoning loop
python scripts/orchestrator.py --process-event test_event.json

# Expected output:
# - Plan.md created
# - Risk classified as medium (new contact)
# - Approval request created
# - Execution paused pending approval
```

**Success Criteria**:
- ✅ Plan.md generated with clear steps
- ✅ Risk level appropriate
- ✅ Approval requested for medium risk
- ✅ All steps logged

### Test 7: End-to-End Workflow

**Objective**: Verify complete workflow from detection to execution

```bash
# Run full integration test
pytest tests/integration/test_watcher_to_skill.py -v

# This test simulates:
# 1. Watcher detects event
# 2. Event file created
# 3. Reasoning loop processes event
# 4. Plan generated
# 5. Risk classified
# 6. Approval requested (if needed)
# 7. Action executed (after approval)
# 8. Task moved to Done/
# 9. All steps logged
```

**Success Criteria**:
- ✅ Complete workflow executes without errors
- ✅ All state transitions correct
- ✅ Files moved to appropriate directories
- ✅ Complete audit trail in logs

---

## Scheduling Setup

### Linux/macOS (cron)

```bash
# Edit crontab
crontab -e

# Add these lines:
# Run watchers every 10 minutes
*/10 * * * * cd /path/to/AI-Employee-Hackathon && /path/to/venv/bin/python scripts/run_watchers.py >> AI_Employee_Vault/Logs/cron.log 2>&1

# Run reasoning loop every 10 minutes
*/10 * * * * cd /path/to/AI-Employee-Hackathon && /path/to/venv/bin/python scripts/orchestrator.py >> AI_Employee_Vault/Logs/cron.log 2>&1

# Generate LinkedIn post weekly (Sunday 9 AM)
0 9 * * 0 cd /path/to/AI-Employee-Hackathon && /path/to/venv/bin/python scripts/linkedin_scheduler.py >> AI_Employee_Vault/Logs/cron.log 2>&1

# Update dashboard daily (8 AM)
0 8 * * * cd /path/to/AI-Employee-Hackathon && /path/to/venv/bin/python scripts/update_dashboard.py >> AI_Employee_Vault/Logs/cron.log 2>&1

# Save and exit
```

### Windows (Task Scheduler)

```powershell
# Run setup script
.\scripts\setup_windows_scheduler.ps1

# This will create scheduled tasks for:
# - Watchers (every 10 minutes)
# - Reasoning loop (every 10 minutes)
# - LinkedIn post generation (weekly)
# - Dashboard update (daily)

# Verify tasks created
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI_Employee*"}
```

### macOS (launchd)

```bash
# Run setup script
./scripts/setup_macos_scheduler.sh

# This will create launchd plists for:
# - Watchers
# - Reasoning loop
# - LinkedIn scheduler
# - Dashboard updater

# Verify agents loaded
launchctl list | grep com.aiemployee
```

---

## Troubleshooting

### Issue: Gmail API Authentication Fails

**Symptoms**: "Authentication failed" error when running gmail_watcher.py

**Solutions**:
1. Verify credentials.json is in correct location
2. Delete token.json and re-authenticate
3. Check Gmail API is enabled in Google Cloud Console
4. Verify OAuth consent screen is configured

### Issue: LinkedIn Login Fails

**Symptoms**: "Login failed" error when testing LinkedIn automation

**Solutions**:
1. Verify credentials in .env are correct
2. Check if LinkedIn account has 2FA enabled (disable or use API mode)
3. Update ChromeDriver to match Chrome version
4. Try running in non-headless mode for debugging

### Issue: WhatsApp QR Code Not Appearing

**Symptoms**: WhatsApp bridge starts but no QR code shown

**Solutions**:
1. Verify Node.js dependencies installed
2. Check whatsapp-web.js version compatibility
3. Clear .wwebjs_auth/ directory and restart
4. Try using qrcode-terminal package for better display

### Issue: Approval Files Not Detected

**Symptoms**: System doesn't detect when approval file is moved

**Solutions**:
1. Verify file permissions on Pending_Approval/ and Approved/ directories
2. Check orchestrator is running and polling
3. Verify file was moved (not copied) to Approved/
4. Check logs for file system errors

### Issue: Logs Not Being Created

**Symptoms**: No log files in Logs/ directory

**Solutions**:
1. Verify Logs/ directory exists and is writable
2. Check LOG_LEVEL in .env
3. Verify logging module is imported correctly
4. Check disk space availability

### Issue: Scheduler Not Running Tasks

**Symptoms**: Scheduled tasks don't execute automatically

**Solutions**:
1. Verify cron service is running (Linux/macOS)
2. Check Task Scheduler service is running (Windows)
3. Verify paths in crontab/scheduled tasks are absolute
4. Check cron.log for error messages
5. Verify virtual environment is activated in scheduled commands

---

## Monitoring and Maintenance

### Daily Checks

```bash
# View dashboard
cat AI_Employee_Vault/Dashboard.md

# Check for pending approvals
ls -la AI_Employee_Vault/Pending_Approval/

# Review recent logs
tail -n 50 AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Weekly Review

```bash
# Generate weekly report
python scripts/generate_weekly_report.py

# Review completed tasks
ls -la AI_Employee_Vault/Done/ | tail -n 20

# Check system health
python scripts/health_check.py
```

### Monthly Maintenance

```bash
# Archive old logs (> 90 days)
python scripts/archive_logs.py --days 90

# Rotate credentials
# 1. Update .env with new credentials
# 2. Re-authenticate Gmail API
# 3. Test LinkedIn login
# 4. Restart MCP servers

# Review and update Business_Goals.md
nano AI_Employee_Vault/Business_Goals.md
```

---

## Next Steps

After completing setup and testing:

1. **Disable DRY_RUN Mode**: Set `DRY_RUN=false` in .env for production
2. **Monitor First Week**: Watch logs closely for first 7 days
3. **Tune Risk Classification**: Adjust risk rules based on false positives/negatives
4. **Optimize Schedules**: Adjust polling intervals based on activity patterns
5. **Expand Watchers**: Add more sources as needed
6. **Document Learnings**: Update this guide with your specific setup notes

---

## Support and Resources

- **Specification**: `specs/001-silver-tier-upgrade/spec.md`
- **Implementation Plan**: `specs/001-silver-tier-upgrade/plan.md`
- **Data Model**: `specs/001-silver-tier-upgrade/data-model.md`
- **MCP Contracts**: `specs/001-silver-tier-upgrade/contracts/`
- **Constitution**: `.specify/memory/constitution.md`

For issues or questions, review the troubleshooting section above or check the logs for detailed error messages.
