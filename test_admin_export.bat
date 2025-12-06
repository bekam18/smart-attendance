@echo off
echo ========================================
echo Testing Admin Export Endpoints
echo ========================================
echo.

echo NOTE: You need to be logged in as admin to test these endpoints.
echo Please login first and copy your JWT token.
echo.

set /p TOKEN="Enter your JWT token (or press Enter to skip): "

if "%TOKEN%"=="" (
    echo.
    echo Skipping API test. Please test from the admin dashboard instead.
    echo.
    echo Steps to test:
    echo 1. Start backend: cd backend ^&^& python app.py
    echo 2. Start frontend: cd frontend ^&^& npm run dev
    echo 3. Login as admin at: http://localhost:5173/login
    echo 4. Go to "All Records" page
    echo 5. Click "Export CSV" or "Export Excel"
    echo.
    pause
    exit /b
)

echo.
echo Testing CSV export...
curl -X GET "http://localhost:5000/api/admin/attendance/export/csv" ^
  -H "Authorization: Bearer %TOKEN%" ^
  --output test_export.csv

echo.
echo.
if exist test_export.csv (
    echo ✅ CSV file created: test_export.csv
    echo File size: 
    dir test_export.csv | find "test_export.csv"
) else (
    echo ❌ CSV export failed
)

echo.
echo ========================================
echo.
echo Testing Excel export...
curl -X GET "http://localhost:5000/api/admin/attendance/export/excel" ^
  -H "Authorization: Bearer %TOKEN%" ^
  --output test_export.xlsx

echo.
echo.
if exist test_export.xlsx (
    echo ✅ Excel file created: test_export.xlsx
    echo File size:
    dir test_export.xlsx | find "test_export.xlsx"
) else (
    echo ❌ Excel export failed
)

echo.
echo ========================================
echo Test complete!
echo.
echo Check the files:
echo - test_export.csv
echo - test_export.xlsx
echo.
pause
