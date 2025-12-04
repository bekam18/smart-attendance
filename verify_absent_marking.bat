@echo off
echo ============================================================
echo Verifying Absent Marking Implementation
echo ============================================================
echo.

echo Checking that the system correctly:
echo 1. Queries students by section and year
echo 2. Marks only non-present students as absent
echo 3. Does not affect students from other sections
echo.

python backend/verify_absent_marking.py

pause
