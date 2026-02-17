# Troubleshooting Guide - AI Employee Silver Tier

**Last Updated**: 2026-02-18
**Version**: Silver Tier 1.0

This guide covers common issues and their solutions for the AI Employee Silver Tier system.

---

## Table of Contents

- [System Won't Start](#system-wont-start)
- [Watcher Issues](#watcher-issues)
- [Approval Workflow Problems](#approval-workflow-problems)
- [MCP Server Issues](#mcp-server-issues)
- [Logging Problems](#logging-problems)
- [Performance Issues](#performance-issues)
- [Scheduler Problems](#scheduler-problems)
- [Skill Errors](#skill-errors)
- [Database/File Issues](#databasefile-issues)
- [Network/Connectivity](#networkconnectivity)

---

## System Won't Start

### Orchestrator Fails to Start

**Symptoms**: `python scripts/orchestrator.py` exits with error

**Common Causes**:
1. Missing dependencies
2. Python version incompatibility
3. Missing directories
4. Configuration errors

**Solutions**:

```bash
# Check Python version (must be 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Verify directory structure
python scripts/health_check.py

# Check for configuration errors
python scripts/validate_constitutional_compliance.py
```

### Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError`

**Solutions**:

```bash
# Ensure you're in project root
pwd

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall in development mode
pip install -e .

# Check PYTHONPATH
echo $PYTHONPATH
```

---

## Watcher Issues

### Gmail Watcher Authentication Fails

**Symptoms**: "Authentication failed" or "Invalid credentials"

**Solutions**:

1. **Re-authenticate**:
   ```bash
   # Delete existing token
   rm AI_Employee_Vault/Watchers/gmail_token.json

   # Re-run authentication
   python AI_Employee_Vault/Watchers/gmail_watcher.py --test
   ```

2. **Verify Gmail API is enabled**:
   - Go to Google Cloud Console
   - Check Gmail API is enabled for your project
   - Verify OAuth consent screen is configured

3. **Check credentials file**:
   ```bash
   # Verify file exists
   ls -la AI_Employee_Vault/Watchers/gmail_credentials.json

   # Check file is valid JSON
   python -m json.tool AI_Employee_Vault/Watchers/gmail_credentials.json
   ```

### LinkedIn Watcher Login Fails

**Symptoms**: "Login failed" or browser automation errors

**Solutions**:

1. **Update ChromeDriver**:
   ```bash
   # Check Chrome version
   google-chrome --version  # Linux
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # macOS

   # Download matching ChromeDriver from:
   # https://chromedriver.chromium.org/
   ```

2. **Disable 2FA temporarily**:
   - LinkedIn 2FA can interfere with automation
   - Consider using LinkedIn API instead

3. **Run in non-headless mode for debugging**:
   ```python
   # Edit AI_Employee_Vault/Watchers/watcher_config.json
   {
     "linkedin": {
       "enabled": true,
       "headless": false  # Change to false
     }
   }
   ```

4. **Check for CAPTCHA**:
   - LinkedIn may show CAPTCHA for automated logins
   - Try logging in manually first
   - Use less frequent polling intervals

### Watcher Not Detecting Events

**Symptoms**: No events created in Needs_Action/

**Solutions**:

```bash
# Test watcher manually
python AI_Employee_Vault/Watchers/gmail_watcher.py --test

# Check watcher configuration
cat AI_Employee_Vault/Watchers/watcher_config.json

# Verify watcher is enabled
python -c "
import json
with open('AI_Employee_Vault/Watchers/watcher_config.json') as f:
    config = json.load(f)
    print('Gmail enabled:', config['gmail']['enabled'])
    print('LinkedIn enabled:', config['linkedin']['enabled'])
"

# Check logs for errors
grep '"component":"watcher"' AI_Employee_Vault/Logs/*.json | grep error
```

---

## Approval Workflow Problems

### Approvals Not Being Detected

**Symptoms**: File moved to Approved/ but system doesn't proceed

**Solutions**:

1. **Verify file was moved (not copied)**:
   ```bash
   # File should NOT exist in Pending_Approval/
   ls AI_Employee_Vault/Pending_Approval/

   # File SHOULD exist in Approved/
   ls AI_Employee_Vault/Approved/
   ```

2. **Check orchestrator is running**:
   ```bash
   # Check if orchestrator process is running
   ps aux | grep orchestrator

   # If not running, start it
   python scripts/orchestrator.py --interval 300
   ```

3. **Check file permissions**:
   ```bash
   # Verify directories are writable
   ls -ld AI_Employee_Vault/{Pending_Approval,Approved,Rejected}

   # Fix permissions if needed
   chmod 755 AI_Employee_Vault/{Pending_Approval,Approved,Rejected}
   ```

### Approval Timeout Not Working

**Symptoms**: Old approvals not auto-rejected after 24 hours

**Solutions**:

```bash
# Check timeout configuration
grep APPROVAL_TIMEOUT .env

# Verify approval workflow is checking timeouts
python -c "
from scripts.approval_workflow import get_approval_workflow
workflow = get_approval_workflow()
pending = workflow.list_pending_approvals()
print(f'Pending approvals: {len(pending)}')
"

# Manually clean up old approvals
python scripts/approval_workflow.py --cleanup-old
```

---

## MCP Server Issues

### Email MCP Server Won't Start

**Symptoms**: "Port already in use" or connection errors

**Solutions**:

1. **Check if port is in use**:
   ```bash
   # Linux/macOS
   lsof -i :5001

   # Windows
   netstat -ano | findstr :5001
   ```

2. **Kill existing process**:
   ```bash
   # Linux/macOS
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   ```

3. **Change port**:
   ```bash
   # Edit .env
   MCP_EMAIL_PORT=5002

   # Restart server
   python mcp_servers/email_server.py
   ```

### LinkedIn MCP Server Selenium Errors

**Symptoms**: "WebDriver not found" or browser errors

**Solutions**:

```bash
# Install/update Selenium
pip install --upgrade selenium

# Verify ChromeDriver is in PATH
which chromedriver  # Linux/macOS
where chromedriver  # Windows

# Test Selenium directly
python -c "
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://www.google.com')
print('Selenium working!')
driver.quit()
"
```

### MCP Server Not Responding

**Symptoms**: Timeout errors when calling MCP server

**Solutions**:

```bash
# Check server is running
ps aux | grep mcp_server

# Test server directly
curl -X POST http://localhost:5001/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'

# Check server logs
tail -f AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | grep mcp

# Restart server
pkill -f email_server.py
python mcp_servers/email_server.py &
```

---

## Logging Problems

### No Logs Being Created

**Symptoms**: Logs/ directory empty or no recent logs

**Solutions**:

```bash
# Verify Logs directory exists and is writable
ls -ld AI_Employee_Vault/Logs/
mkdir -p AI_Employee_Vault/Logs/
chmod 755 AI_Employee_Vault/Logs/

# Check LOG_LEVEL in .env
grep LOG_LEVEL .env

# Test logger directly
python -c "
from scripts.logger import get_logger
logger = get_logger()
logger.info(
    component='test',
    action='test_log',
    actor='troubleshooter',
    target='system',
    details={'test': True}
)
print('Log entry created')
"

# Check today's log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Log Files Too Large

**Symptoms**: Disk space issues, slow log reading

**Solutions**:

```bash
# Check log file sizes
du -sh AI_Employee_Vault/Logs/*.json

# Run log rotation
python scripts/archive_logs.py

# Configure automatic rotation in cron
# Add to crontab:
# 0 2 * * * cd /path/to/project && python scripts/archive_logs.py
```

### Corrupted Log Files

**Symptoms**: JSON parse errors when reading logs

**Solutions**:

```bash
# Find corrupted lines
python -c "
import json
from pathlib import Path

log_file = Path('AI_Employee_Vault/Logs/2026-02-18.json')
with open(log_file) as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line.strip())
        except json.JSONDecodeError as e:
            print(f'Line {i}: {e}')
"

# Backup and fix
cp AI_Employee_Vault/Logs/2026-02-18.json AI_Employee_Vault/Logs/2026-02-18.json.bak
# Manually remove corrupted lines
```

---

## Performance Issues

### Slow Event Processing

**Symptoms**: Events take > 30 seconds to process

**Solutions**:

```bash
# Check system resources
top
htop

# Analyze processing times
python scripts/performance_validation.py

# Check for stale tasks
python scripts/watchdog.py

# Reduce concurrent task limit
# Edit scripts/orchestrator.py
# Change max_concurrent_tasks to lower value

# Optimize polling intervals
# Edit .env
WATCHER_INTERVAL_MINUTES=15  # Increase from 10
```

### High Memory Usage

**Symptoms**: System using excessive RAM

**Solutions**:

```bash
# Check memory usage
free -h  # Linux
vm_stat  # macOS

# Find memory-hungry processes
ps aux --sort=-%mem | head -10

# Restart orchestrator periodically
# Add to cron:
# 0 */6 * * * pkill -f orchestrator.py && sleep 5 && python scripts/orchestrator.py &

# Clear old tasks
find AI_Employee_Vault/Done/ -mtime +30 -delete
```

### Disk Space Issues

**Symptoms**: "No space left on device" errors

**Solutions**:

```bash
# Check disk usage
df -h

# Find large files
du -sh AI_Employee_Vault/* | sort -h

# Archive old logs
python scripts/archive_logs.py --days 30

# Clean up old tasks
find AI_Employee_Vault/Done/ -mtime +90 -delete

# Compress archives
gzip AI_Employee_Vault/Logs/archive/*.json
```

---

## Scheduler Problems

### Cron Jobs Not Running

**Symptoms**: Scheduled tasks don't execute automatically

**Solutions**:

```bash
# Verify cron service is running
systemctl status cron  # Linux
launchctl list | grep cron  # macOS

# Check crontab entries
crontab -l

# Verify paths are absolute
# BAD:  */10 * * * * python scripts/orchestrator.py
# GOOD: */10 * * * * cd /full/path && /full/path/venv/bin/python scripts/orchestrator.py

# Check cron logs
grep CRON /var/log/syslog  # Linux
log show --predicate 'process == "cron"' --last 1h  # macOS

# Test command manually
cd /path/to/project && /path/to/venv/bin/python scripts/orchestrator.py --once
```

### Windows Task Scheduler Not Working

**Symptoms**: Scheduled tasks don't run on Windows

**Solutions**:

```powershell
# Check Task Scheduler service
Get-Service -Name "Schedule"

# List AI Employee tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI_Employee*"}

# Check task history
Get-ScheduledTask -TaskName "AI_Employee_Orchestrator" | Get-ScheduledTaskInfo

# Re-run setup script as Administrator
.\scripts\setup_windows_scheduler.ps1

# Test task manually
Start-ScheduledTask -TaskName "AI_Employee_Orchestrator"
```

### macOS launchd Issues

**Symptoms**: launchd agents not running

**Solutions**:

```bash
# Check if agents are loaded
launchctl list | grep com.aiemployee

# Load agent manually
launchctl load ~/Library/LaunchAgents/com.aiemployee.orchestrator.plist

# Check agent status
launchctl list com.aiemployee.orchestrator

# View agent logs
tail -f ~/Library/Logs/com.aiemployee.orchestrator.log

# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.aiemployee.orchestrator.plist
launchctl load ~/Library/LaunchAgents/com.aiemployee.orchestrator.plist
```

---

## Skill Errors

### Skill Not Found

**Symptoms**: "Skill not found" or routing errors

**Solutions**:

```bash
# List available skills
ls -la .claude/skills/

# Verify skill structure
ls -la .claude/skills/reasoning-loop/
# Should contain: SKILL.md, prompt.txt, examples.md

# Check orchestrator routing
grep -A 10 "_route_to_skill" scripts/orchestrator.py

# Test skill directly
python -c "
from pathlib import Path
skill_dir = Path('.claude/skills/reasoning-loop')
print('Skill exists:', skill_dir.exists())
print('SKILL.md:', (skill_dir / 'SKILL.md').exists())
print('prompt.txt:', (skill_dir / 'prompt.txt').exists())
"
```

### Skill Execution Fails

**Symptoms**: Skill invoked but fails to execute

**Solutions**:

```bash
# Check logs for skill errors
grep '"actor":"reasoning-loop"' AI_Employee_Vault/Logs/*.json | grep error

# Verify skill dependencies
# Check if skill requires specific MCP servers or files

# Test skill components individually
python scripts/plan_generator.py --test
python scripts/step_executor.py --test

# Check DRY_RUN mode
grep DRY_RUN .env
# If DRY_RUN=true, skills will simulate actions
```

---

## Database/File Issues

### File Lock Errors

**Symptoms**: "Resource temporarily unavailable" or lock errors

**Solutions**:

```bash
# Check for stale lock files
find AI_Employee_Vault/ -name "*.lock"

# Remove stale locks (be careful!)
find AI_Employee_Vault/ -name "*.lock" -mmin +60 -delete

# Check for processes holding locks
lsof AI_Employee_Vault/Needs_Action/*.json

# Restart orchestrator
pkill -f orchestrator.py
sleep 5
python scripts/orchestrator.py &
```

### Corrupted Task Files

**Symptoms**: JSON parse errors, invalid task format

**Solutions**:

```bash
# Find corrupted files
for file in AI_Employee_Vault/Needs_Action/*.json; do
    python -m json.tool "$file" > /dev/null 2>&1 || echo "Corrupted: $file"
done

# Move corrupted files to quarantine
mkdir -p AI_Employee_Vault/Quarantine
mv corrupted_file.json AI_Employee_Vault/Quarantine/

# Validate all task files
python scripts/validate_task_files.py
```

---

## Network/Connectivity

### Gmail API Rate Limiting

**Symptoms**: "Quota exceeded" or rate limit errors

**Solutions**:

```bash
# Increase polling interval
# Edit AI_Employee_Vault/Watchers/watcher_config.json
{
  "gmail": {
    "poll_interval": 900  # Increase to 15 minutes
  }
}

# Check quota usage in Google Cloud Console
# Navigate to: APIs & Services > Gmail API > Quotas

# Implement exponential backoff
# Already implemented in gmail_watcher.py
```

### LinkedIn Connection Issues

**Symptoms**: "Connection refused" or timeout errors

**Solutions**:

```bash
# Check internet connectivity
ping linkedin.com

# Verify LinkedIn is accessible
curl -I https://www.linkedin.com

# Check for IP blocking
# LinkedIn may block automated access
# Solution: Use less frequent polling, add delays

# Use proxy if needed
# Edit mcp_servers/linkedin_server.py
# Add proxy configuration to Selenium
```

---

## Getting More Help

### Diagnostic Commands

Run these commands to gather diagnostic information:

```bash
# System health check
python scripts/health_check.py

# Constitutional compliance
python scripts/validate_constitutional_compliance.py

# Performance validation
python scripts/performance_validation.py

# Security audit
python scripts/security_audit.py

# Bronze tier verification
python scripts/verify_bronze_tier.py

# Quickstart validation
python scripts/validate_quickstart.py
```

### Log Analysis

```bash
# View today's errors
grep '"status":"error"' AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq .

# Count events by component
jq -r '.component' AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | sort | uniq -c

# Find slow operations (> 5 seconds)
jq 'select(.details.duration_ms > 5000)' AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Track specific event
grep '"target":"gmail_20260218_001"' AI_Employee_Vault/Logs/*.json | jq .
```

### Support Resources

- **Documentation**: `specs/001-silver-tier-upgrade/`
- **README**: `README.md`
- **Contributing**: `CONTRIBUTING.md`
- **Verification Report**: `VERIFICATION_REPORT.md`

---

**Last Updated**: 2026-02-18
**Version**: Silver Tier 1.0
