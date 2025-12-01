@echo off
echo ========================================
echo Prepare Large Dataset Structure
echo ========================================
echo.
echo This script will:
echo 1. Validate folder names (must be student IDs like STU013)
echo 2. Check for nested subfolders
echo 3. Count images per student
echo 4. Provide recommendations
echo.
echo ========================================
echo.

cd backend

python prepare_large_dataset.py

echo.
pause
