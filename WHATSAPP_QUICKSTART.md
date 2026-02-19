# WhatsApp Integration - Quick Start

## Overview

WhatsApp has been successfully integrated as the third watcher for the Silver Tier AI Employee system. The integration follows the same architecture as Gmail and LinkedIn watchers, with automatic integration into the reasoning loop and approval workflow.

## What Was Implemented

### 1. Core Components

- **`AI_Employee_Vault/Watchers/whatsapp_watcher.py`**: Python watcher that monitors WhatsApp messages
- **`whatsapp_bridge.js`**: Node.js bridge server using whatsapp-web.js for WhatsApp Web automation
- **`package.json`**: Node.js dependencies configuration

### 2. Integration Points

- **`scripts/run_watchers.py`**: Updated to include WhatsApp watcher
- **`AI_Employee_Vault/Watchers/watcher_config.json`**: WhatsApp configuration already present
- **`.env.example`**: WhatsApp environment variables added
- **`.gitignore`**: Node.js and WhatsApp session files excluded

### 3. Documentation & Tools

- **`WHATSAPP_SETUP.md`**: Comprehensive setup and troubleshooting guide
- **`verify_whatsapp.py`**: Verification script to check installation

## Architecture

```
WhatsApp Message
    ↓
WhatsApp Web (Browser)
    ↓
whatsapp_bridge.js (Node.js)
    ↓ HTTP API
whatsapp_watcher.py (Python)
    ↓ Event File
AI_Employee_Vault/Needs_Action/
    ↓
Reasoning Loop (Claude Skill)
    ↓
Plan.md Generation
    ↓
Step Execution
    ↓
Approval Workflow (if needed)
    ↓
Action Execution
    ↓
AI_Employee_Vault/Done/
```

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Verify Python dependencies are installed
pip install -r requirements.txt
```

### Step 2: Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# WHATSAPP_ENABLED=true
```

Edit `AI_Employee_Vault/Watchers/watcher_config.json`:
```json
{
  "watchers": {
    "whatsapp": {
      "enabled": true,
      "poll_interval_seconds": 300,
      "bridge_url": "http://localhost:5002",
      "features": {
        "personal_messages": true,
        "group_messages": false
      }
    }
  }
}
```

### Step 3: Start Bridge & Authenticate

```bash
# Start the WhatsApp bridge
node whatsapp_bridge.js

# Scan QR code with WhatsApp on your phone
# (QR code will display in terminal)
```

### Step 4: Test

```bash
# Verify installation
python verify_whatsapp.py

# Test the watcher
python scripts/run_watchers.py --watcher whatsapp --test

# Send yourself a WhatsApp message and run again
```

### Step 5: Run in Production

```bash
# Run all watchers (Gmail, LinkedIn, WhatsApp)
python scripts/run_watchers.py
```

## How It Works

### Message Detection

1. WhatsApp message arrives → Bridge captures it
2. Watcher polls bridge every 5 minutes (configurable)
3. New messages normalized to standard event format
4. Event file created in `Needs_Action/`

### Reasoning Loop Processing

The existing reasoning loop automatically processes WhatsApp events:

1. **Event Analysis**: Classifies message (sales, support, complaint, etc.)
2. **Plan Generation**: Creates `Plan.md` for complex tasks
3. **Step Execution**: Executes planned actions systematically
4. **Progress Tracking**: Updates `Plan.md` after each step

### Approval Workflow

WhatsApp replies follow the Human-in-the-Loop (HITL) process:

1. Reasoning loop drafts reply
2. Reply saved to `Pending_Approval/`
3. Human reviews and approves/rejects (by moving file)
4. If approved → Reply sent via bridge
5. All actions logged in `Logs/`

## Event Format

WhatsApp messages are normalized to this format:

```json
{
  "event_id": "20260220_143022_whatsapp_a3f8d1",
  "source": "whatsapp",
  "type": "whatsapp_message",
  "timestamp": "2026-02-20T14:30:22Z",
  "priority": "medium",
  "content": {
    "subject": "WhatsApp from John Doe",
    "body": "Message content here",
    "from": "John Doe",
    "to": "me"
  },
  "metadata": {
    "message_id": "...",
    "from_number": "1234567890@c.us",
    "is_group": false,
    "contact_history": "known",
    "labels": ["whatsapp", "personal"]
  }
}
```

## Integration with Existing Skills

WhatsApp events automatically integrate with all existing Claude skills:

- **`reasoning-loop`**: Analyzes messages and generates plans
- **`task-orchestrator`**: Manages multi-step workflows
- **`approval-guard`**: Enforces HITL for sensitive actions
- **`logging-audit`**: Logs all WhatsApp interactions
- **`email-mcp-sender`**: Can send follow-up emails based on WhatsApp messages

## Constitutional Compliance

The WhatsApp integration follows all constitutional principles:

- ✅ **Local-First**: All messages processed locally, session stored in `.wwebjs_auth/`
- ✅ **HITL Safety**: Replies require approval via `Pending_Approval/` workflow
- ✅ **Proactivity**: Automatically monitors and responds to messages
- ✅ **Persistence**: Continues processing until task completion
- ✅ **Transparency**: All actions logged in `Logs/`
- ✅ **Cost Efficiency**: Automated monitoring reduces manual work

## Scheduling

Add to your scheduler (cron/Task Scheduler):

```bash
# Run watchers every 5 minutes
*/5 * * * * cd /path/to/project && python scripts/run_watchers.py

# Or run specific watcher
*/5 * * * * cd /path/to/project && python scripts/run_watchers.py --watcher whatsapp
```

**Important**: The Node.js bridge must be running continuously:
- Run as a system service (systemd on Linux)
- Run as a startup task (Task Scheduler on Windows)
- See `WHATSAPP_SETUP.md` for detailed instructions

## Troubleshooting

### Bridge Not Starting
```bash
# Check if dependencies are installed
npm install

# Check if port is available
netstat -an | grep 5002
```

### Authentication Issues
```bash
# Delete session and re-authenticate
rm -rf .wwebjs_auth/
node whatsapp_bridge.js
# Scan new QR code
```

### No Messages Detected
```bash
# Check bridge status
curl http://localhost:5002/health

# Check watcher connectivity
python AI_Employee_Vault/Watchers/whatsapp_watcher.py --check-bridge

# Send test message and check bridge logs
```

### Watcher Errors
```bash
# Check logs
tail -f AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Run verification script
python verify_whatsapp.py
```

## Security Notes

- **Session Security**: WhatsApp session stored locally in `.wwebjs_auth/` (gitignored)
- **Message Privacy**: All processing happens locally, never sent to external services
- **Approval Required**: All replies require human approval before sending
- **Audit Trail**: Complete log of all WhatsApp interactions in `Logs/`

## Next Steps

1. **Test End-to-End**: Send a test message and verify it creates an event
2. **Review Plan.md**: Check that reasoning loop generates proper plans
3. **Test Approval**: Verify approval workflow for reply actions
4. **Monitor Logs**: Review `Logs/` to ensure proper logging
5. **Production Deploy**: Set up bridge as a service and schedule watchers

## Files Modified/Created

### Created
- `AI_Employee_Vault/Watchers/whatsapp_watcher.py`
- `whatsapp_bridge.js`
- `package.json`
- `WHATSAPP_SETUP.md`
- `verify_whatsapp.py`
- `WHATSAPP_QUICKSTART.md` (this file)

### Modified
- `scripts/run_watchers.py` (added WhatsApp watcher import and initialization)
- `.env.example` (added WhatsApp configuration)
- `.gitignore` (added Node.js and WhatsApp session exclusions)

### Unchanged (Already Compatible)
- `AI_Employee_Vault/Watchers/watcher_config.json` (already had WhatsApp config)
- `.claude/skills/reasoning-loop/` (automatically processes WhatsApp events)
- `scripts/approval_workflow.py` (automatically handles WhatsApp approvals)
- All other existing skills and infrastructure

## Support

For detailed documentation, see:
- **Setup Guide**: `WHATSAPP_SETUP.md`
- **Architecture**: `specs/001-silver-tier-upgrade/plan.md`
- **Verification**: Run `python verify_whatsapp.py`

## Version

- **WhatsApp Integration**: v1.0.0
- **Implementation Date**: 2026-02-20
- **Silver Tier**: Functional Assistant Stage
