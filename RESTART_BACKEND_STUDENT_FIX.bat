@echo off
echo ========================================
echo Restarting Backend - Student Dashboard Fix
echo ========================================
echo.

echo Stopping any running backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul

echo.
echo Starting backend...
cd backend
start "SmartAttendance Backend" python app.py

echo.
echo Backend restarted!
echo Check the new window for backend logs
echo.
pause
