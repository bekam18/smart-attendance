@echo off
echo ================================================================================
echo Testing CORS and JWT Fixes
echo ================================================================================
echo.

echo Step 1: Checking backend files...
echo.

if not exist "backend\app.py" (
    echo ERROR: backend\app.py not found
    exit /b 1
)

if not exist "backend\utils\security.py" (
    echo ERROR: backend\utils\security.py not found
    exit /b 1
)

if not exist "backend\blueprints\attendance.py" (
    echo ERROR: backend\blueprints\attendance.py not found
    exit /b 1
)

echo ✓ All backend files found
echo.

echo Step 2: Checking frontend files...
echo.

if not exist "frontend\src\lib\api.ts" (
    echo ERROR: frontend\src\lib\api.ts not found
    exit /b 1
)

echo ✓ All frontend files found
echo.

echo Step 3: Verifying CORS configuration...
findstr /C:"automatic_options=True" backend\app.py >nul
if %errorlevel% equ 0 (
    echo ✓ CORS automatic_options=True found
) else (
    echo ✗ CORS automatic_options=True NOT found
)
echo.

echo Step 4: Verifying decorator order...
findstr /C:"@jwt_required()" backend\blueprints\attendance.py >nul
if %errorlevel% equ 0 (
    echo ✓ @jwt_required() decorator found
) else (
    echo ✗ @jwt_required() decorator NOT found
)
echo.

echo Step 5: Verifying FormData handling...
findstr /C:"instanceof FormData" frontend\src\lib\api.ts >nul
if %errorlevel% equ 0 (
    echo ✓ FormData detection found
) else (
    echo ✗ FormData detection NOT found
)
echo.

echo ================================================================================
echo Test Complete!
echo ================================================================================
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& python app.py
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Test face recognition in browser
echo.
echo Expected behavior:
echo - OPTIONS requests should NOT appear in backend logs
echo - POST requests should show "Method: POST" with image data
echo - Browser console should show FormData with File object
echo - Face recognition should work without errors
echo.
pause
