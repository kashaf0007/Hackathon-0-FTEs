# Windows Task Scheduler Setup Script for AI Employee
# Run this script as Administrator in PowerShell

param(
    [switch]$Remove,
    [switch]$DryRun
)

Write-Host "🔧 AI Employee Scheduler Setup (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Error: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Get project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Check Python installation
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✅ Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found" -ForegroundColor Red
    Write-Host "   Please install Python 3.11+ and add to PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Task definitions
$tasks = @(
    @{
        Name = "AI_Employee_Orchestrator"
        Description = "AI Employee main orchestration loop"
        Script = "scripts\orchestrator.py"
        Arguments = "--once"
        Schedule = "Every 5 minutes"
        Trigger = @{
            Type = "Daily"
            At = "00:00"
            RepetitionInterval = "PT5M"
            RepetitionDuration = "P1D"
        }
    },
    @{
        Name = "AI_Employee_Watchers"
        Description = "AI Employee event watchers"
        Script = "scripts\run_watchers.py"
        Arguments = ""
        Schedule = "Every 10 minutes"
        Trigger = @{
            Type = "Daily"
            At = "00:00"
            RepetitionInterval = "PT10M"
            RepetitionDuration = "P1D"
        }
    },
    @{
        Name = "AI_Employee_Dashboard"
        Description = "AI Employee dashboard update"
        Script = "scripts\update_dashboard.py"
        Arguments = ""
        Schedule = "Daily at 8:00 AM"
        Trigger = @{
            Type = "Daily"
            At = "08:00"
        }
    },
    @{
        Name = "AI_Employee_Watchdog"
        Description = "AI Employee health check"
        Script = "scripts\watchdog.py"
        Arguments = ""
        Schedule = "Daily at 9:00 AM"
        Trigger = @{
            Type = "Daily"
            At = "09:00"
        }
    },
    @{
        Name = "AI_Employee_LinkedIn"
        Description = "AI Employee LinkedIn post generation"
        Script = "scripts\linkedin_scheduler.py"
        Arguments = ""
        Schedule = "Weekly Monday at 9:00 AM"
        Trigger = @{
            Type = "Weekly"
            DaysOfWeek = "Monday"
            At = "09:00"
        }
    }
)

# Remove existing tasks if requested
if ($Remove) {
    Write-Host "🗑️  Removing existing AI Employee tasks..." -ForegroundColor Yellow
    Write-Host ""

    foreach ($task in $tasks) {
        try {
            Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false -ErrorAction SilentlyContinue
            Write-Host "   ✅ Removed: $($task.Name)" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️  Not found: $($task.Name)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "✅ Removal complete" -ForegroundColor Green
    exit 0
}

# Create log directory
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
    Write-Host "✅ Created logs directory" -ForegroundColor Green
} else {
    Write-Host "✅ Logs directory exists" -ForegroundColor Green
}

Write-Host ""

# Create scheduled tasks
Write-Host "📝 Creating scheduled tasks..." -ForegroundColor Cyan
Write-Host ""

foreach ($task in $tasks) {
    $taskName = $task.Name
    $scriptPath = Join-Path $ProjectRoot $task.Script
    $logFile = Join-Path $LogDir "$taskName.log"

    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "   ⚠️  Task already exists: $taskName" -ForegroundColor Yellow
        Write-Host "      Run with -Remove to remove existing tasks first" -ForegroundColor Yellow
        continue
    }

    if ($DryRun) {
        Write-Host "   [DRY RUN] Would create: $taskName" -ForegroundColor Cyan
        Write-Host "      Schedule: $($task.Schedule)" -ForegroundColor Gray
        continue
    }

    # Create action
    $pythonExe = (Get-Command python).Source
    $arguments = "$scriptPath $($task.Arguments) >> `"$logFile`" 2>&1"
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument $arguments -WorkingDirectory $ProjectRoot

    # Create trigger
    $trigger = $null
    if ($task.Trigger.Type -eq "Daily") {
        $trigger = New-ScheduledTaskTrigger -Daily -At $task.Trigger.At

        if ($task.Trigger.RepetitionInterval) {
            $trigger.Repetition = New-ScheduledTaskTrigger -Once -At $task.Trigger.At -RepetitionInterval $task.Trigger.RepetitionInterval -RepetitionDuration $task.Trigger.RepetitionDuration | Select-Object -ExpandProperty Repetition
        }
    } elseif ($task.Trigger.Type -eq "Weekly") {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $task.Trigger.DaysOfWeek -At $task.Trigger.At
    }

    # Create settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Register task
    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $task.Description -ErrorAction Stop | Out-Null
        Write-Host "   ✅ Created: $taskName" -ForegroundColor Green
        Write-Host "      Schedule: $($task.Schedule)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Failed: $taskName" -ForegroundColor Red
        Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""

# Display created tasks
Write-Host "📋 Installed tasks:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

foreach ($task in $tasks) {
    $scheduledTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
    if ($scheduledTask) {
        $status = $scheduledTask.State
        $statusColor = if ($status -eq "Ready") { "Green" } else { "Yellow" }
        Write-Host "   $($task.Name): " -NoNewline
        Write-Host $status -ForegroundColor $statusColor
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Verify tasks: Get-ScheduledTask | Where-Object {`$_.TaskName -like 'AI_Employee*'}" -ForegroundColor Gray
Write-Host "   2. Check logs in: $LogDir" -ForegroundColor Gray
Write-Host "   3. Monitor execution: Get-Content $LogDir\AI_Employee_Orchestrator.log -Wait" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Note: Make sure DRY_RUN is set appropriately in .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "To remove all tasks: .\setup_windows_scheduler.ps1 -Remove" -ForegroundColor Gray
Write-Host ""
