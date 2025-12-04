@echo off
echo Testing sections-by-course endpoint...
echo.

REM Get instructor token first
echo Getting instructor token...
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"instructor@example.com\",\"password\":\"password123\"}" ^
  -o token_response.json

echo.
echo Token response saved to token_response.json
echo.

REM Extract token (manual step - copy token from token_response.json)
echo Please copy the token from token_response.json and run:
echo.
echo curl -X GET "http://localhost:5000/api/instructor/sections-by-course?course_name=CS101" ^
echo   -H "Authorization: Bearer YOUR_TOKEN_HERE"
echo.

pause
