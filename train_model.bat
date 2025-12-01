@echo off
echo ========================================
echo Face Recognition Model Training
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting training process...
echo Dataset: backend/dataset
echo Output: backend/models/Classifier
echo.

python train_model.py --dataset dataset --output models/Classifier --classifier svm --threshold-percentile 95

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Training completed successfully!
    echo ========================================
    echo.
    echo Model files saved to: backend/models/Classifier/
    echo - face_classifier.pkl
    echo - label_encoder.pkl
    echo - model_metadata.pkl
    echo.
    echo You can now start the backend server.
) else (
    echo ========================================
    echo Training failed!
    echo ========================================
    echo Please check the error messages above.
)

pause
