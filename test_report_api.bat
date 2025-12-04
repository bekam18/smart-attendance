@echo off
echo Testing Report Generation API...
echo.

REM First login to get token
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"ba\",\"password\":\"password\"}" ^
  -o login_response.json

echo Login response saved to login_response.json
echo.

REM Extract token (you'll need to manually copy it)
type login_response.json
echo.
echo.
echo Copy the access_token from above and paste it below:
set /p TOKEN="Enter token: "

echo.
echo Testing report generation...
curl -X POST http://localhost:5000/api/instructor/reports/generate ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"report_type\":\"daily\",\"section_id\":\"A\",\"course_name\":\"Mobile Development\",\"start_date\":\"2025-12-04\",\"end_date\":\"2025-12-04\"}"

echo.
pause
