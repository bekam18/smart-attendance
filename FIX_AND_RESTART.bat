@echo off
echo ========================================
echo Fix Students.py and Restart Backend
echo ========================================
echo.

echo Step 1: Restoring correct students.py file...
copy /Y backend\blueprints\students_fixed.py backend\blueprints\students.py
echo ✓ File restored
echo.

echo Step 2: Stopping any running backend...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo ✓ Backend stopped
echo.

echo Step 3: Starting backend...
cd backend
start "SmartAttendance Backend" cmd /k "python app.py"
cd ..
echo ✓ Backend started in new window
echo.

echo ========================================
echo DONE!
echo ========================================
echo.
echo The backend is now running in a separate window.
echo.
echo Next steps:
echo 1. Check the backend window for any errors
echo 2. Open http://localhost:5173 in your browser
echo 3. Login as a student
echo 4. The dashboard should now work!
echo.
echo ⚠️ WARNING: Do not let IDE autofix modify students.py!
echo.
pause
