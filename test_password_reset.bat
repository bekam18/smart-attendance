@echo off
echo ========================================
echo Testing Password Reset Feature
echo ========================================
echo.

echo Step 1: Testing forgot-password endpoint
echo.
curl -X POST http://localhost:5000/api/auth/forgot-password ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@smartattendance.com\"}"
echo.
echo.

echo ========================================
echo.
echo If email is configured, check your inbox.
echo If not configured, copy the token from console above.
echo.
echo Then test the reset link:
echo http://localhost:5173/reset-password?token=YOUR_TOKEN
echo.
echo ========================================
pause
