@echo off
echo ========================================
echo Production Model Training
echo ========================================
echo.
echo Dataset: backend/dataset/processed/
echo Output: backend/models/Classifier/
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing/updating dependencies...
pip install torch torchvision facenet-pytorch tqdm --quiet

echo.
echo Starting training...
echo ========================================
python train_production_model.py --dataset dataset/processed --output models/Classifier --classifier svm --threshold-percentile 95

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Training completed successfully!
    echo ========================================
    echo.
    echo Model files saved to: backend/models/Classifier/
    echo - face_classifier_v1.pkl
    echo - label_encoder_classes.npy
    echo - X.npy
    echo - y.npy
    echo - training_metadata.json
    echo - training_summary.txt
    echo.
    echo Next steps:
    echo 1. Test model: cd backend ^&^& python test_production_model.py --test-all
    echo 2. Start backend: python app.py
    echo 3. Test live recognition in frontend
    echo.
) else (
    echo ========================================
    echo Training failed!
    echo ========================================
    echo Please check the error messages above.
    echo Check training.log for details.
)

pause
