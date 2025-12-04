@echo off
echo Installing openpyxl for Excel report generation...
echo ================================================
echo.

cd backend
pip install openpyxl==3.1.2

echo.
echo Installation complete!
echo.
echo You can now use the Download Reports feature with Excel export.
pause
