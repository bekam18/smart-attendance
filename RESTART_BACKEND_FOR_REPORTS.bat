@echo off
echo ========================================
echo   RESTART BACKEND FOR REPORTS FIX
echo ========================================
echo.
echo This will restart the backend server to enable the reports feature.
echo.
echo INSTRUCTIONS:
echo 1. Close the current backend terminal (Ctrl+C)
echo 2. Run this file to start the backend again
echo.
pause

echo Starting backend...
cd backend
python app.py
