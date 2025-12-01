@echo off
echo ========================================
echo Attendance Fields Migration
echo ========================================
echo.
echo This script will update existing attendance records
echo with year, course, and session_type from their sessions
echo.
pause

cd backend
python migrate_attendance_fields.py

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
pause
