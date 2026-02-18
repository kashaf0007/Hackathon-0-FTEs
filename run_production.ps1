# PowerShell script to run AI Employee in production mode
# Usage: .\run_production.ps1

$env:DRY_RUN = "false"
$env:PYTHONPATH = $PWD

Write-Host "Running AI Employee Orchestrator in PRODUCTION mode..." -ForegroundColor Red
Write-Host "DRY_RUN=$env:DRY_RUN" -ForegroundColor Yellow
Write-Host "PYTHONPATH=$env:PYTHONPATH" -ForegroundColor Yellow
Write-Host ""

python scripts/orchestrator.py --interval 300
