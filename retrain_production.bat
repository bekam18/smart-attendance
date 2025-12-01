@echo off
echo ========================================
echo SmartAttendance Production Model Training
echo ========================================
echo.
echo Using existing production training pipeline
echo.
pause

cd backend
python train_production_model.py

echo.
echo ========================================
echo Training Complete!
echo ========================================
pause
