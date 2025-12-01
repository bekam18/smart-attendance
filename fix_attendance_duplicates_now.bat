@echo off
echo ========================================
echo FIX DUPLICATE ATTENDANCE - ALL IN ONE
echo ========================================
echo.
echo This will:
echo 1. Remove duplicate attendance records
echo 2. Add unique database index
echo 3. Prevent future duplicates
echo.
echo ========================================
echo.

cd backend

echo Step 1: Cleaning up duplicates...
echo ========================================
python cleanup_duplicate_attendance.py

echo.
echo.
echo Step 2: Adding unique index...
echo ========================================
python add_unique_index.py

echo.
echo.
echo ========================================
echo FIX COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your backend server
echo 2. Start a new attendance session
echo 3. Test - student should appear only ONCE per session
echo.
pause
