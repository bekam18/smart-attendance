@echo off
echo ========================================
echo RESTART BACKEND TO ENABLE ABSENT MARKING
echo ========================================
echo.
echo STEP 1: Stop the current backend
echo - Go to the terminal where backend is running
echo - Press Ctrl+C to stop it
echo.
pause
echo.
echo STEP 2: Starting backend with new code...
echo.
cd backend
python app.py
