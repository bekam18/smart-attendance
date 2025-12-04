@echo off
echo ========================================
echo Testing Section Filter
echo ========================================
echo.

echo Step 1: Login as instructor
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"instructor1\",\"password\":\"password123\"}" ^
  -o login_response.json
echo.

echo Step 2: Extract token (check login_response.json manually)
echo.

echo Step 3: Test filter with Section A
echo Replace YOUR_TOKEN with actual token from login_response.json
echo curl -X GET "http://localhost:5000/api/instructor/records?section_id=A" -H "Authorization: Bearer YOUR_TOKEN"
echo.

echo Step 4: Test filter with Section C
echo curl -X GET "http://localhost:5000/api/instructor/records?section_id=C" -H "Authorization: Bearer YOUR_TOKEN"
echo.

echo ========================================
echo Check login_response.json for token
echo Then run the curl commands above with your token
echo ========================================
pause
