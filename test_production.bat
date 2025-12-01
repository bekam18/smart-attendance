@echo off
echo ========================================
echo Production Model Testing
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Testing trained model...
echo ========================================
python test_production_model.py --test-all

echo.
echo ========================================
echo Testing complete!
echo ========================================
echo.
echo Check the results above.
echo If accuracy is good, you can start the backend server.
echo.

pause
