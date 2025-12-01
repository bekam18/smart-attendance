@echo off
echo ================================================================================
echo RETRAIN MODEL WITH FIXED PREPROCESSING
echo ================================================================================
echo.
echo This will:
echo 1. Delete OLD model files
echo 2. Retrain with L2 normalization
echo 3. Test the new model
echo.
pause
echo.

cd backend

echo ================================================================================
echo STEP 1: Deleting Old Model Files
echo ================================================================================
echo.

if exist "models\Classifier\face_classifier_v1.pkl" (
    echo Deleting: face_classifier_v1.pkl
    del /F /Q "models\Classifier\face_classifier_v1.pkl"
)

if exist "models\Classifier\label_encoder.pkl" (
    echo Deleting: label_encoder.pkl
    del /F /Q "models\Classifier\label_encoder.pkl"
)

if exist "models\Classifier\label_encoder_classes.npy" (
    echo Deleting: label_encoder_classes.npy
    del /F /Q "models\Classifier\label_encoder_classes.npy"
)

if exist "models\Classifier\X.npy" (
    echo Deleting: X.npy
    del /F /Q "models\Classifier\X.npy"
)

if exist "models\Classifier\y.npy" (
    echo Deleting: y.npy
    del /F /Q "models\Classifier\y.npy"
)

if exist "models\Classifier\training_metadata.json" (
    echo Deleting: training_metadata.json
    del /F /Q "models\Classifier\training_metadata.json"
)

if exist "models\Classifier\training_summary.txt" (
    echo Deleting: training_summary.txt
    del /F /Q "models\Classifier\training_summary.txt"
)

echo.
echo ✓ Old model files deleted
echo.

echo ================================================================================
echo STEP 2: Training Fixed Model
echo ================================================================================
echo.
echo Training with L2-normalized embeddings...
echo This will take 5-10 minutes depending on dataset size.
echo.

python train_fixed_model.py --threshold-percentile 10

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
echo STEP 3: Testing Fixed Model
echo ================================================================================
echo.

python test_fixed_model.py

echo.
echo ================================================================================
echo COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo 1. If all tests passed, restart your backend
echo 2. Test face recognition in the frontend
echo.
echo Expected confidence scores:
echo - Known faces: 0.70-0.99
echo - Unknown faces: below 0.50
echo.
pause
