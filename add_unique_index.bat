@echo off
echo ========================================
echo Add Unique Index to Attendance Collection
echo ========================================
echo.
echo This will add a database-level constraint to prevent duplicates.
echo.
echo IMPORTANT: Run cleanup_duplicates.bat FIRST if you have existing duplicates!
echo.
echo ========================================
echo.

cd backend
python add_unique_index.py

echo.
echo ========================================
echo Done!
echo ========================================
pause
