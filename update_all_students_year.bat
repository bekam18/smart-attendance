@echo off
echo ========================================
echo Update All Students to 4th Year
echo ========================================
echo.
echo This will update ALL students to:
echo - Year Level: 4th Year
echo.
pause

cd backend
python update_all_students_year.py
cd ..

echo.
echo ========================================
echo Update Complete
echo ========================================
pause
