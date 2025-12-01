@echo off
echo ========================================
echo Installing InsightFace Dependencies
echo ========================================
echo.
echo This will install:
echo - insightface==0.7.3
echo - onnxruntime==1.16.3
echo.
pause

cd backend
pip install insightface==0.7.3
pip install onnxruntime==1.16.3

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo InsightFace detector is now ready to use.
echo The system will automatically use InsightFace
echo for better face detection accuracy.
echo.
pause
