Write-Host "Collecting codebase files for review..." -ForegroundColor Green
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
python collect_codebase.py
Write-Host "Done! Check codebase_for_review.txt for the collected code." -ForegroundColor Green
Read-Host "Press Enter to exit"
