@echo off
echo ========================================
echo SmartAttendance Clean Retrain
echo ========================================
echo.
echo This will:
echo 1. Delete all previous model artifacts
echo 2. Extract embeddings using InsightFace + FaceNet
echo 3. Train new SVM classifier
echo 4. Generate training report
echo.
pause

python retrain_model.py

echo.
echo ========================================
echo Retraining Complete
echo ========================================
pause
