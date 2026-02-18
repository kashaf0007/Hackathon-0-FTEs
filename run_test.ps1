# PowerShell script to run AI Employee in test mode
# Usage: .\run_test.ps1

$env:DRY_RUN = "true"
$env:PYTHONPATH = $PWD

Write-Host "Running AI Employee Orchestrator in TEST mode..." -ForegroundColor Green
Write-Host "DRY_RUN=$env:DRY_RUN" -ForegroundColor Yellow
Write-Host "PYTHONPATH=$env:PYTHONPATH" -ForegroundColor Yellow
Write-Host ""

python scripts/orchestrator.py --once
