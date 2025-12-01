#!/bin/bash

echo "🚀 SmartAttendance Setup Script"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Backend
echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.sample .env
    echo "✅ Created backend/.env file"
fi

# Create necessary directories
mkdir -p models/Classifier uploads

cd ..

# Setup Frontend
echo ""
echo "📦 Setting up Frontend..."
cd frontend

# Install dependencies
npm install

# Create .env file
if [ ! -f .env ]; then
    cp .env.sample .env
    echo "✅ Created frontend/.env file"
fi

cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Place your trained model files in backend/models/Classifier/"
echo "2. Update backend/.env with your MongoDB connection string"
echo "3. Run the backend: cd backend && python app.py"
echo "4. Run the frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker: docker-compose up --build"
