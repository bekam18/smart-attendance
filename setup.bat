@echo off
echo ========================================
echo SmartAttendance Setup Script (Windows)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo [OK] Prerequisites check passed
echo.

REM Setup Backend
echo ========================================
echo Setting up Backend...
echo ========================================
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file
if not exist .env (
    echo Creating backend\.env file...
    copy .env.sample .env
)

REM Create necessary directories
if not exist models\Classifier mkdir models\Classifier
if not exist uploads mkdir uploads

cd ..

REM Setup Frontend
echo.
echo ========================================
echo Setting up Frontend...
echo ========================================
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env file
if not exist .env (
    echo Creating frontend\.env file...
    copy .env.sample .env
)

cd ..

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Place your trained model files in backend\models\Classifier\
echo 2. Update backend\.env with your MongoDB connection string
echo 3. Run the backend: cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo 4. Run the frontend: cd frontend ^&^& npm run dev
echo.
echo Or use Docker: docker-compose up --build
echo.
pause
