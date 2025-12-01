@echo off
echo ========================================
echo Cleanup Duplicate Attendance Records
echo ========================================
echo.
echo This script will:
echo 1. Find duplicate attendance records
echo 2. Keep only the LATEST entry per student per session
echo 3. Delete older duplicate entries
echo 4. Update session attendance counts
echo.
echo ========================================
echo.

cd backend
python cleanup_duplicate_attendance.py

echo.
echo ========================================
echo Done!
echo ========================================
pause
