@echo off
echo ========================================
echo Testing Student Dashboard Endpoints
echo ========================================
echo.

echo Step 1: Login as a student
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"student1\",\"password\":\"password123\"}" ^
  -o student_login.json
echo.

echo Check student_login.json for the token
echo.

echo Step 2: Test profile endpoint
echo curl -X GET http://localhost:5000/api/students/profile -H "Authorization: Bearer YOUR_TOKEN"
echo.

echo Step 3: Test attendance endpoint
echo curl -X GET http://localhost:5000/api/students/attendance -H "Authorization: Bearer YOUR_TOKEN"
echo.

echo Step 4: Test attendance stats endpoint
echo curl -X GET http://localhost:5000/api/students/attendance/stats -H "Authorization: Bearer YOUR_TOKEN"
echo.

pause
