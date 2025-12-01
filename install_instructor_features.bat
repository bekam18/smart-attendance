@echo off
echo ========================================
echo Installing Instructor Features
echo ========================================
echo.

echo Step 1: Installing openpyxl for Excel export...
cd backend
pip install openpyxl
cd ..

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your backend: cd backend ^&^& python app.py
echo 2. Open http://localhost:5173
echo 3. Login as instructor
echo 4. You'll see "View Records" and "Settings" buttons
echo.
echo Features available:
echo - View attendance records with filtering
echo - Export to CSV and Excel
echo - Adjust confidence threshold
echo - Change password
echo.
pause
