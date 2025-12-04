@echo off
echo Testing Instructor Reports Feature
echo ===================================
echo.

echo 1. Testing report generation endpoint...
curl -X POST http://localhost:5000/api/instructor/reports/generate ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"report_type\":\"daily\",\"section_id\":\"A\",\"course_name\":\"web\",\"start_date\":\"2025-12-01\",\"end_date\":\"2025-12-04\"}"
echo.
echo.

echo 2. Testing CSV download endpoint...
echo (This will download a file if successful)
curl -X POST http://localhost:5000/api/instructor/reports/download/csv ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"report_type\":\"weekly\",\"section_id\":\"A\",\"course_name\":\"web\",\"start_date\":\"2025-12-01\",\"end_date\":\"2025-12-07\"}" ^
  --output test_report.csv
echo.
echo.

echo 3. Testing Excel download endpoint...
echo (This will download a file if successful)
curl -X POST http://localhost:5000/api/instructor/reports/download/excel ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"report_type\":\"monthly\",\"section_id\":\"A\",\"course_name\":\"web\",\"start_date\":\"2025-12-01\",\"end_date\":\"2025-12-31\"}" ^
  --output test_report.xlsx
echo.
echo.

echo Testing complete!
echo.
echo Note: Replace YOUR_TOKEN_HERE with actual JWT token from login
echo You can get the token by logging in through the frontend and checking localStorage
pause
