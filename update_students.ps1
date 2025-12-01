Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Update Student Database with Real List" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "- Remove all test students"
Write-Host "- Add 19 real students"
Write-Host "- Preserve admin/instructor accounts"
Write-Host "- Keep other collections unchanged"
Write-Host ""
Write-Host "Sections:" -ForegroundColor Yellow
Write-Host "- Section A: STU001-STU006 (6 students)"
Write-Host "- Section B: STU008-STU014 (7 students)"
Write-Host "- Section C: STU015-STU021 (6 students)"
Write-Host ""

$continue = Read-Host "Continue? (y/n)"
if ($continue -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Running update script..." -ForegroundColor Green

# Check if in virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "Warning: No virtual environment detected" -ForegroundColor Yellow
    Write-Host "Attempting to activate venv..." -ForegroundColor Yellow
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Host "Virtual environment activated" -ForegroundColor Green
    }
}

# Run the update script
Set-Location backend
python update_real_students.py
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Update Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Students can now login with:" -ForegroundColor Yellow
Write-Host "- Username: Their student_id (e.g., STU001)"
Write-Host "- Password: {FirstName}123 (e.g., Nabila123)"
Write-Host ""
Write-Host "Next: Students should register their faces" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
