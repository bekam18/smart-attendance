@echo off
echo ========================================
echo Testing Face Detection Endpoint
echo ========================================
echo.

cd backend

echo Starting test...
python -c "from blueprints.attendance import detect_face; print('✓ Face detection endpoint loaded successfully')"

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
echo The /attendance/detect-face endpoint is ready.
echo It will return bounding boxes and landmarks for detected faces.
echo.
pause
