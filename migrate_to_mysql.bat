@echo off
echo ========================================
echo MongoDB to MySQL Migration
echo ========================================
echo.
echo This script will help you migrate from MongoDB to MySQL
echo.
echo REQUIREMENTS:
echo - MySQL server installed and running
echo - MySQL database 'smart_attendance' created
echo - MongoDB still running (for data migration)
echo.
echo ========================================
echo.

pause

echo Step 1: Installing MySQL connector...
echo ========================================
cd backend
pip install mysql-connector-python==9.1.0

echo.
echo Step 2: Setting up environment...
echo ========================================
if not exist .env (
    echo Creating .env file from example...
    copy .env.mysql.example .env
    echo.
    echo IMPORTANT: Edit backend\.env and add your MySQL password!
    echo.
    pause
)

echo.
echo Step 3: Running data migration...
echo ========================================
echo Make sure MongoDB is running!
echo.
pause

python migrate_mongo_to_mysql.py

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Verify your .env file has correct MySQL credentials
echo 2. Test the backend: python app.py
echo 3. Check the migration guide: MYSQL_MIGRATION_COMPLETE_GUIDE.md
echo.
pause
