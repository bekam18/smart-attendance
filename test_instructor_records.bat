@echo off
echo Testing instructor records endpoint...
echo.

curl -X GET "http://127.0.0.1:5000/api/instructor/records" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -H "Content-Type: application/json"

echo.
echo.
pause
