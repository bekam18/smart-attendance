@echo off
echo ========================================
echo Update Student Information
echo ========================================
echo.
echo This will update:
echo - Group 1 (STU001-STU013): Section A, 4th Year
echo - Group 2 (STU014-STU019, STU021): Section B, 4th Year
echo - Fix STU021 name to "Yien"
echo.
pause

cd backend
python update_student_info.py
cd ..

echo.
echo ========================================
echo Update Complete
echo ========================================
pause
