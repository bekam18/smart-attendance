@echo off
echo ========================================
echo Multi-Instructor Security Migration
echo ========================================
echo.
echo This will update your database to support
echo secure multi-instructor access control.
echo.
echo Changes:
echo - Add sections to instructors
echo - Add instructor_id to sessions
echo - Add instructor_id to attendance records
echo - Add section_id to sessions and attendance
echo.
pause

cd backend
python migrate_instructor_security.py

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart backend: python app.py
echo 2. Test multi-instructor access
echo 3. Verify data isolation
echo.
pause
