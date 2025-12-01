@echo off
echo ========================================
echo Update Student Database with Real List
echo ========================================
echo.
echo This will:
echo - Remove all test students
echo - Add 19 real students
echo - Preserve admin/instructor accounts
echo - Keep other collections unchanged
echo.
echo Sections:
echo - Section A: STU001-STU006 (6 students)
echo - Section B: STU008-STU014 (7 students)
echo - Section C: STU015-STU021 (6 students)
echo.
pause

echo.
echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    cd backend
    python update_real_students.py
    cd ..
) else (
    echo Virtual environment not found. Running with system Python...
    cd backend
    python update_real_students.py
    cd ..
)

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Students can now login with:
echo - Username: Their student_id (e.g., STU001)
echo - Password: {FirstName}123 (e.g., Nabila123)
echo.
echo Next: Students should register their faces
echo.
pause
