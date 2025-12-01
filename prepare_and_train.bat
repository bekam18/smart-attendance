@echo off
echo ========================================
echo Face Recognition Training Workflow
echo ========================================
echo.

cd backend

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Validating dataset...
echo ========================================
python prepare_dataset.py --validate
echo.

set /p continue="Continue with training? (y/n): "
if /i not "%continue%"=="y" (
    echo Training cancelled.
    pause
    exit /b
)

echo.
echo Step 3: Training model...
echo ========================================
python train_model.py --dataset dataset --output models/Classifier --classifier svm --threshold-percentile 95

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Training failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo Step 4: Testing trained model...
echo ========================================
python test_trained_model.py --test-all

echo.
echo ========================================
echo Workflow Complete!
echo ========================================
echo.
echo Model files saved to: backend/models/Classifier/
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Test face recognition in attendance session
echo.

pause
