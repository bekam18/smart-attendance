@echo off
echo ================================================================================
echo CLEAN OLD MODEL FILES
echo ================================================================================
echo.
echo This script will DELETE all old model files to ensure clean retraining.
echo.
echo WARNING: This will remove:
echo   - backend/models/Classifier/*
echo   - backend/models/Embeddings/*
echo   - backend/models/FaceNet/*
echo   - backend/models/MTCNN/*
echo.
echo The .gitkeep files will be preserved to maintain folder structure.
echo.
pause
echo.

echo Cleaning Classifier models...
if exist "backend\models\Classifier" (
    for %%F in (backend\models\Classifier\*) do (
        if not "%%~nxF"==".gitkeep" (
            echo Deleting: %%F
            del /F /Q "%%F"
        )
    )
    echo ✓ Classifier folder cleaned
) else (
    echo ⚠ Classifier folder not found
)
echo.

echo Cleaning Embeddings models...
if exist "backend\models\Embeddings" (
    for %%F in (backend\models\Embeddings\*) do (
        if not "%%~nxF"==".gitkeep" (
            echo Deleting: %%F
            del /F /Q "%%F"
        )
    )
    echo ✓ Embeddings folder cleaned
) else (
    echo ⚠ Embeddings folder not found
)
echo.

echo Cleaning FaceNet models...
if exist "backend\models\FaceNet" (
    for %%F in (backend\models\FaceNet\*) do (
        if not "%%~nxF"==".gitkeep" (
            echo Deleting: %%F
            del /F /Q "%%F"
        )
    )
    echo ✓ FaceNet folder cleaned
) else (
    echo ⚠ FaceNet folder not found
)
echo.

echo Cleaning MTCNN models...
if exist "backend\models\MTCNN" (
    for %%F in (backend\models\MTCNN\*) do (
        if not "%%~nxF"==".gitkeep" (
            echo Deleting: %%F
            del /F /Q "%%F"
        )
    )
    echo ✓ MTCNN folder cleaned
) else (
    echo ⚠ MTCNN folder not found
)
echo.

echo ================================================================================
echo CLEANUP COMPLETE
echo ================================================================================
echo.
echo All old model files have been deleted.
echo You can now run train_production.bat to retrain with clean models.
echo.
pause
