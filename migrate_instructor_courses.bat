@echo off
echo ========================================
echo Migrating Instructors to Multi-Course Format
echo ========================================
echo.

cd backend
python migrate_instructor_courses.py

echo.
echo ========================================
echo Migration Complete!
echo ========================================
pause
