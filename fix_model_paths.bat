@echo off
echo ========================================
echo SmartAttendance - Model Path Fixer
echo ========================================
echo.

cd backend

echo Checking model directory...
if not exist "models\Classifier" (
    echo Creating model directory...
    mkdir models\Classifier
    echo ✅ Created: models\Classifier
) else (
    echo ✅ Model directory exists
)
echo.

echo Checking model files...
echo.

if exist "models\Classifier\face_classifier_v1.pkl" (
    echo ✅ face_classifier_v1.pkl found
) else (
    echo ❌ face_classifier_v1.pkl NOT FOUND
    if exist "models\Classifier\classifier.pkl" (
        echo 💡 Found classifier.pkl - renaming...
        ren "models\Classifier\classifier.pkl" "face_classifier_v1.pkl"
        echo ✅ Renamed to face_classifier_v1.pkl
    )
)
echo.

if exist "models\Classifier\label_encoder.pkl" (
    echo ✅ label_encoder.pkl found
) else (
    echo ❌ label_encoder.pkl NOT FOUND
    if exist "models\Classifier\encoder.pkl" (
        echo 💡 Found encoder.pkl - renaming...
        ren "models\Classifier\encoder.pkl" "label_encoder.pkl"
        echo ✅ Renamed to label_encoder.pkl
    )
)
echo.

if exist "models\Classifier\label_encoder_classes.npy" (
    echo ✅ label_encoder_classes.npy found
) else (
    echo ❌ label_encoder_classes.npy NOT FOUND
    if exist "models\Classifier\classes.npy" (
        echo 💡 Found classes.npy - renaming...
        ren "models\Classifier\classes.npy" "label_encoder_classes.npy"
        echo ✅ Renamed to label_encoder_classes.npy
    )
)
echo.

echo ========================================
echo Running verification script...
echo ========================================
echo.

python verify_models.py

echo.
echo ========================================
echo Done!
echo ========================================
pause
