@echo off
echo ============================================================
echo Fixing Year Format in Existing Sessions
echo ============================================================
echo.
echo This will update sessions with year='4' to year='4th Year'
echo so that absent marking works correctly.
echo.

python backend/fix_session_year_format.py

echo.
pause
