@echo off
echo ================================================================================
echo ATTENDANCE RECORDING RULES VERIFICATION
echo ================================================================================
echo.

echo 1. Checking attendance table schema...
python check_attendance_schema.py
echo.

echo 2. Checking sessions table schema...
python check_sessions_schema.py
echo.

echo 3. Testing attendance recording rules...
python test_attendance_rules.py
echo.

echo ================================================================================
echo VERIFICATION COMPLETE
echo ================================================================================
pause
