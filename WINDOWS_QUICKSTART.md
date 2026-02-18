# Quick Start Guide for Windows PowerShell

## Test Mode (Recommended First)

### Option 1: Using PowerShell script
```powershell
.\run_test.ps1
```

### Option 2: Manual commands
```powershell
$env:DRY_RUN = "true"
$env:PYTHONPATH = $PWD
python scripts/orchestrator.py --once
```

## Production Mode

### Option 1: Using PowerShell script
```powershell
.\run_production.ps1
```

### Option 2: Manual commands
```powershell
$env:DRY_RUN = "false"
$env:PYTHONPATH = $PWD
python scripts/orchestrator.py --interval 300
```

## Test Individual Components

```powershell
# Set PYTHONPATH first
$env:PYTHONPATH = $PWD

# Test Gmail watcher
python AI_Employee_Vault/Watchers/gmail_watcher.py --test

# Test LinkedIn watcher
python AI_Employee_Vault/Watchers/linkedin_watcher.py --test

# System health check
python scripts/watchdog.py

# Update dashboard
python scripts/update_dashboard.py
```

## Troubleshooting

If you get import errors, make sure to set PYTHONPATH:
```powershell
$env:PYTHONPATH = $PWD
```

To make it permanent for the session:
```powershell
$env:PYTHONPATH = (Get-Location).Path
```
