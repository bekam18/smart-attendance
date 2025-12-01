@echo off
echo ========================================
echo Verifying Absent Marking Implementation
echo ========================================
echo.
echo Checking if the code is in place...
echo.

cd backend
python -c "from blueprints.attendance import end_session; import inspect; code = inspect.getsource(end_session); print('✓ end_session function found'); print('✓ Checking for absent marking logic...'); assert 'absent_student_ids' in code, 'Absent marking logic missing!'; assert 'status.*absent' in code or \"'absent'\" in code, 'Absent status missing!'; print('✓ Absent marking logic is present'); print('✓ Code implementation verified!')"

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. RESTART the backend server:
echo    - Stop the current backend (Ctrl+C)
echo    - Run: cd backend
echo    - Run: python app.py
echo.
echo 2. Test the feature:
echo    - Login as instructor
echo    - Start a session for a section
echo    - End the session
echo    - Check attendance records
echo.
echo 3. Or run automated test:
echo    - Run: test_absent_marking.bat
echo.
pause
