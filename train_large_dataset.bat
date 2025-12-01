@echo off
echo ========================================
echo Train with LARGE Dataset (100-200 images per student)
echo ========================================
echo.
echo This script will:
echo 1. Use ALL images from each student folder
echo 2. Apply L2 normalization + StandardScaler
echo 3. Train SVM with probability and class balancing
echo 4. Calculate optimal threshold automatically
echo 5. Save model with high accuracy
echo.
echo Requirements:
echo - Dataset structure: backend/dataset/STU###/images
echo - 100-200 images per student recommended
echo.
echo ========================================
echo.

cd backend

echo Starting training...
echo.

python train_large_dataset.py

echo.
echo ========================================
echo Training Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Test model: python test_production_model.py
echo 2. Restart backend: python app.py
echo 3. Test in UI
echo.
pause
