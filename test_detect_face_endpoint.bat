@echo off
echo Testing Face Detection Endpoint
echo ================================
echo.

cd backend

echo Testing if endpoint is accessible...
python -c "from blueprints.attendance import detect_face; print('✓ detect_face function exists')"

echo.
echo Checking route registration...
python -c "from app import app; routes = [str(rule) for rule in app.url_map.iter_rules() if 'detect' in str(rule)]; print('Routes with detect:', routes)"

echo.
echo ================================
echo.
echo If you see the route listed above, the endpoint exists.
echo If you see 404 errors, check:
echo 1. Backend is running
echo 2. URL is correct: /api/attendance/detect-face
echo 3. JWT token is valid
echo.
pause
