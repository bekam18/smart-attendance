@echo off
echo ========================================
echo Fix Embedding Dimension Mismatch
echo ========================================
echo.

echo Problem: Your model expects 512 features but
echo the system generates 44 features.
echo.
echo This script will rebuild your model to match
echo the current embedding generator (44 features).
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

cd backend

echo Generating embeddings from face images...
python generate_embeddings_and_train.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ SUCCESS!
    echo ========================================
    echo.
    echo Your model has been rebuilt to match the
    echo current embedding generator.
    echo.
    echo Next steps:
    echo 1. Restart backend: python app.py
    echo 2. Test recognition
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ ERROR!
    echo ========================================
    echo.
    echo Model rebuilding failed.
    echo.
    echo Common issues:
    echo - No face images in uploads/faces/
    echo - Not enough images per student
    echo - Images don't contain faces
    echo.
    echo See FIX_EMBEDDING_MISMATCH.md for details.
    echo.
)

pause
