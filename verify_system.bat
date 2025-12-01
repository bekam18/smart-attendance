@echo off
echo ========================================
echo SmartAttendance - System Verification
echo ========================================
echo.

echo Checking backend server...
curl -s http://localhost:5000/health
echo.
echo.

echo Checking model status...
curl -s http://localhost:5000/api/debug/model-status
echo.
echo.

echo Testing admin login...
curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo Testing instructor login...
curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"instructor\",\"password\":\"inst123\"}"
echo.
echo.

echo Testing student login...
curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"student\",\"password\":\"stud123\"}"
echo.
echo.

echo ========================================
echo Verification Complete!
echo.
echo Check above for:
echo - Health: should return {"status":"healthy"}
echo - Model: should show model_loaded status
echo - Logins: should return access_token for each role
echo ========================================
pause
