@echo off
echo ========================================
echo SmartAttendance - Role Testing Script
echo ========================================
echo.

echo Testing Admin Login...
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo Testing Instructor Login...
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"instructor\",\"password\":\"inst123\"}"
echo.
echo.

echo Testing Student Login...
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"student\",\"password\":\"stud123\"}"
echo.
echo.

echo ========================================
echo All three roles should return tokens
echo Check backend terminal for debug logs
echo ========================================
pause
