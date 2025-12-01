@echo off
echo ================================================================================
echo FIX LOW CONFIDENCE ISSUE - Complete Pipeline
echo ================================================================================
echo.
echo This script will:
echo 1. Diagnose embedding distribution mismatch
echo 2. Clean old model files
echo 3. Retrain model with fixed preprocessing
echo 4. Test the new model
echo 5. Verify confidence scores
echo.
echo ⚠️  WARNING: This will DELETE all existing model files!
echo.
pause
echo.

cd backend

echo ================================================================================
echo STEP 1: Diagnosing Current Model
echo ================================================================================
echo.
python diagnose_embedding_mismatch.py
echo.
echo Press any key to continue with cleanup and retraining...
pause
echo.

echo ================================================================================
echo STEP 2: Cleaning Old Model Files
echo ================================================================================
echo.

if exist "models\Classifier\face_classifier_v1.pkl" (
    echo Deleting: models\Classifier\face_classifier_v1.pkl
    del /F /Q "models\Classifier\face_classifier_v1.pkl"
)

if exist "models\Classifier\label_encoder_classes.npy" (
    echo Deleting: models\Classifier\label_encoder_classes.npy
    del /F /Q "models\Classifier\label_encoder_classes.npy"
)

if exist "models\Classifier\X.npy" (
    echo Deleting: models\Classifier\X.npy
    del /F /Q "models\Classifier\X.npy"
)

if exist "models\Classifier\y.npy" (
    echo Deleting: models\Classifier\y.npy
    del /F /Q "models\Classifier\y.npy"
)

if exist "models\Classifier\training_metadata.json" (
    echo Deleting: models\Classifier\training_metadata.json
    del /F /Q "models\Classifier\training_metadata.json"
)

if exist "models\Classifier\training_summary.txt" (
    echo Deleting: models\Classifier\training_summary.txt
    del /F /Q "models\Classifier\training_summary.txt"
)

echo.
echo ✓ Old model files deleted
echo.

echo ================================================================================
echo STEP 3: Training Fixed Model
echo ================================================================================
echo.
echo Training with L2-normalized embeddings...
echo This ensures training and inference use identical preprocessing.
echo.

python train_fixed_model.py --threshold-percentile 5

if %errorlevel% neq 0 (
    echo.
    echo ❌ Training failed!
    echo Check training_fixed.log for details
    pause
    exit /b 1
)

echo.
echo ✓ Training complete
echo.

echo ================================================================================
echo STEP 4: Testing Fixed Model
echo ================================================================================
echo.

python test_fixed_model.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Some tests failed
    echo Review the output above
    echo.
)

echo.
echo ================================================================================
echo STEP 5: Final Diagnosis
echo ================================================================================
echo.

python diagnose_embedding_mismatch.py

echo.
echo ================================================================================
echo COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo 1. Review the test results above
echo 2. If all tests passed, restart your backend:
echo    cd backend
echo    python app.py
echo 3. Test face recognition in the frontend
echo.
echo Expected behavior:
echo - Confidence scores should be 0.70-0.99 for known faces
echo - Unknown faces should have confidence below threshold
echo - No more "everything is unknown" issue
echo.
pause
