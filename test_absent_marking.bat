@echo off
echo ========================================
echo Testing Automatic Absent Marking
echo ========================================
echo.
echo This test will verify that when an instructor ends a session,
echo students who didn't appear on camera are automatically marked as absent.
echo.
echo Prerequisites:
echo - Backend server must be running
echo - You must have an active session
echo - Students must be in the database with section and year
echo.
pause

cd backend
python test_absent_marking.py
pause
