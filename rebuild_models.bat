@echo off
echo ========================================
echo SmartAttendance - Model Rebuilder
echo ========================================
echo.

cd backend

echo This script will rebuild your model files to fix the
echo "invalid load key, 'x'" error.
echo.
echo It will:
echo 1. Load your existing dataset (X.npy, y.npy)
echo 2. Train a new classifier compatible with Python 3.10.11
echo 3. Save new model files
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

echo Running rebuild script...
echo.

python rebuild_models.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ SUCCESS!
    echo ========================================
    echo.
    echo Your models have been rebuilt successfully!
    echo.
    echo Next steps:
    echo 1. Verify models: python verify_models.py
    echo 2. Start backend: python app.py
    echo 3. Test recognition
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ ERROR!
    echo ========================================
    echo.
    echo Model rebuilding failed. Check the output above for details.
    echo.
    echo Common issues:
    echo - X.npy or y.npy not found
    echo - Not enough samples in dataset
    echo - scikit-learn not installed
    echo.
    echo See REBUILD_MODELS_GUIDE.md for troubleshooting.
    echo.
)

pause
