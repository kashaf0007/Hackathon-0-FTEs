# AI Employee - Quick Reference Guide

## Running the System

### Test Mode (Safe - No Real Actions)
```powershell
.\run_test.ps1
```

### Production Mode (Real Actions)
```powershell
.\run_production.ps1
```

### Manual Commands
```powershell
# Set environment
$env:PYTHONPATH = $PWD
$env:DRY_RUN = "true"

# Run once
python scripts/orchestrator.py --once

# Run continuously (5-minute cycles)
python scripts/orchestrator.py --interval 300
```

## Creating Tasks

Tasks are JSON files in `AI_Employee_Vault/Needs_Action/`

### Task Template
```json
{
  "event_id": "YYYYMMDD_taskname_001",
  "source": "manual",
  "created_at": "2026-02-18T12:00:00Z",
  "processed": false,
  "event_type": "task_type",
  "priority": "LOW|MEDIUM|HIGH",
  "data": {
    "title": "Task Title",
    "description": "What needs to be done",
    "context": "Additional context"
  }
}
```

### Example Task Types
- `draft_email` - Draft an email response
- `research` - Research a topic
- `summarize` - Summarize content
- `analyze` - Analyze data or situation
- `schedule` - Schedule a task
- `reminder` - Create a reminder

## Monitoring

### Check System Health
```powershell
$env:PYTHONPATH = $PWD
python scripts/watchdog.py
```

### View Dashboard
```powershell
Get-Content AI_Employee_Vault/Dashboard.md
```

### View Logs
```powershell
# Today's logs
Get-Content "AI_Employee_Vault/Logs/$(Get-Date -Format 'yyyy-MM-dd').json"

# Search for errors
Select-String -Path "AI_Employee_Vault/Logs/*.json" -Pattern '"status":"error"'
```

## Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/       # Tasks to be processed (JSON files)
├── Done/               # Completed tasks
├── Pending_Approval/   # Tasks awaiting approval
├── Approved/           # Approved tasks
├── Rejected/           # Rejected tasks
├── Logs/               # Daily logs (YYYY-MM-DD.json)
├── Dashboard.md        # System status dashboard
├── Business_Goals.md   # Your business objectives
└── Plan.md            # Current execution plan
```

## Enabling Watchers

### Gmail Watcher
1. Follow instructions in `GMAIL_SETUP.md`
2. Get OAuth credentials from Google Cloud Console
3. Save as `AI_Employee_Vault/Watchers/gmail_credentials.json`
4. Run authentication: `python AI_Employee_Vault/Watchers/gmail_watcher.py --authenticate`
5. Enable in `AI_Employee_Vault/Watchers/watcher_config.json`

### LinkedIn Watcher
1. Add credentials to `.env`:
   ```
   LINKEDIN_EMAIL=your-email@example.com
   LINKEDIN_PASSWORD=your-password
   ```
2. Install Chrome/Chromium browser
3. Enable in `AI_Employee_Vault/Watchers/watcher_config.json`

## Troubleshooting

### Import Errors
```powershell
$env:PYTHONPATH = $PWD
```

### Unicode/Emoji Errors
Already fixed in orchestrator with UTF-8 encoding

### Watcher Errors
Disable watchers in config if you don't have credentials:
```json
"gmail": { "enabled": false }
"linkedin": { "enabled": false }
```

## Files Created During Setup

- `run_test.ps1` - Test mode launcher
- `run_production.ps1` - Production mode launcher
- `WINDOWS_QUICKSTART.md` - Windows setup guide
- `GMAIL_SETUP.md` - Gmail API setup guide
- `TEST_RESULTS.md` - Setup verification results
- `TEST_WITHOUT_CREDENTIALS.md` - Testing without external services
- `scripts/__init__.py` - Python package files (4 total)

## Next Steps

1. ✅ System is working - test with custom tasks
2. 📧 Set up Gmail API (optional) - see `GMAIL_SETUP.md`
3. 💼 Set up LinkedIn (optional) - add credentials to `.env`
4. 📝 Edit `AI_Employee_Vault/Business_Goals.md` with your objectives
5. 🚀 Run in production mode when ready

## Support

- Check logs: `AI_Employee_Vault/Logs/`
- View dashboard: `AI_Employee_Vault/Dashboard.md`
- Run health check: `python scripts/watchdog.py`
- Review README: `README.md`
