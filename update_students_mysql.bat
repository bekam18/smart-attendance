@echo off
echo ========================================
echo Update Students for MySQL
echo ========================================
echo.
echo This will replace test students with 19 real students
echo.
pause

cd backend
python update_real_students_mysql.py

echo.
echo ========================================
echo.
pause
