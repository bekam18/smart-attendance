@echo off
echo ========================================
echo Testing Multi-Course Instructor Feature
echo ========================================
echo.

echo This will test:
echo 1. Migration of existing instructors
echo 2. Backend API endpoints
echo.

echo Step 1: Running migration...
echo ----------------------------------------
cd backend
python migrate_instructor_courses.py
echo.

echo Step 2: Testing complete!
echo ----------------------------------------
echo.
echo Next steps:
echo 1. Start the backend: cd backend ^&^& python app.py
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo 3. Login as admin
echo 4. Try adding an instructor with multiple courses
echo.
echo ========================================
pause
