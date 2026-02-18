# Quick Test Without External Credentials

## Test the core system without Gmail/LinkedIn:

```powershell
# Set environment
$env:PYTHONPATH = $PWD
$env:DRY_RUN = "true"

# Test 1: Run orchestrator once (should work without watchers)
python scripts/orchestrator.py --once

# Test 2: Check system health
python scripts/watchdog.py

# Test 3: Update dashboard
python scripts/update_dashboard.py

# Test 4: Create a manual test task
# Create a file in AI_Employee_Vault/Needs_Action/ with this content:
```

## Create Test Task Manually

Create file: `AI_Employee_Vault/Needs_Action/test_task_001.md`

```markdown
# Test Task

**Type**: test
**Priority**: LOW
**Created**: 2026-02-18T10:00:00
**Status**: PENDING

## Context
This is a test task to verify the orchestrator is working.

## Expected Output
Task should be processed and moved to Done folder.
```

## Run the orchestrator to process it:
```powershell
$env:PYTHONPATH = $PWD
$env:DRY_RUN = "true"
python scripts/orchestrator.py --once
```

## Check the logs:
```powershell
# View today's log
Get-Content "AI_Employee_Vault/Logs/$(Get-Date -Format 'yyyy-MM-dd').json"
```
