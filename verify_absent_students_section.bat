@echo off
echo ============================================================
echo Verifying Absent Students Are From Correct Section
echo ============================================================
echo.

echo This script checks that:
echo 1. Absent students in attendance records match the session's section
echo 2. No students from other sections are marked absent
echo 3. The section/year data is displayed correctly in records
echo.

python backend/verify_absent_students_section.py

echo.
pause
