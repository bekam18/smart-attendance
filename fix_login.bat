@echo off
echo ========================================
echo SmartAttendance - Fix Login Issue
echo ========================================
echo.

cd backend

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Checking database status...
python check_db.py

echo.
echo ========================================
echo.
echo If you saw "No users found", run this command:
echo   python seed_db.py
echo.
echo Then restart your backend server:
echo   python app.py
echo.
echo ========================================
pause
