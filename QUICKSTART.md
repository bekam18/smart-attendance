# Quick Start Guide

Get SmartAttendance up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd SmartAttendance

# Make setup script executable (Linux/Mac)
chmod +x setup.sh

# Run setup script
./setup.sh
```

Or manually:

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env

# Frontend setup
cd ../frontend
npm install
cp .env.sample .env
```

## Step 2: Configure Environment

### Backend (.env)

Edit `backend/.env`:

```env
MONGODB_URI=mongodb+srv://bekamayela18_db_user:2qBIVM2Qn3IZDAQy@cluster0.ifaywcg.mongodb.net/
MONGODB_DB_NAME=smart_attendance
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
RECOGNITION_THRESHOLD=0.60
```

### Frontend (.env)

Edit `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:5000
```

## Step 3: Add Model Files

Place your trained model files in `backend/models/Classifier/`:

```
backend/models/Classifier/
├── face_classifier_v1.pkl
├── label_encoder.pkl
└── label_encoder_classes.npy
```

**Don't have model files?** The system will still run but recognition will use fallback features.

## Step 4: Seed Database

```bash
cd backend
python seed_db.py
```

This creates demo users:
- Admin: `admin` / `admin123`
- Instructor: `instructor` / `inst123`
- Student: `student` / `stud123`

## Step 5: Run the Application

### Option A: Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

### Option B: Docker

```bash
docker-compose up --build
```

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:5000

## Step 6: Login and Test

1. Open http://localhost:5173 (or http://localhost for Docker)
2. Login with demo credentials:
   - **Admin:** `admin` / `admin123`
   - **Instructor:** `instructor` / `inst123`
   - **Student:** `student` / `stud123`

## Testing the System

### As Admin:
1. View dashboard statistics
2. Add new instructors
3. View all students
4. Monitor attendance records

### As Instructor:
1. Create a new attendance session
2. Start camera for live recognition
3. System will automatically capture and recognize faces
4. View attendance list in real-time

### As Student:
1. View attendance history
2. Register face images (if not already registered)
3. Check attendance statistics

## Quick Test Without Camera

Use the debug endpoint to test recognition:

```bash
# Test with an image
curl -X POST -F "image=@test_face.jpg" \
  http://localhost:5000/api/debug/recognition-test
```

## Common First-Time Issues

### Backend won't start
- Check MongoDB connection string
- Ensure port 5000 is available
- Verify Python dependencies installed

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and reinstall
- Verify port 5173 is available

### Camera not working
- Grant browser camera permissions
- Use HTTPS in production
- Try different browser

### Recognition not working
- Verify model files are present
- Check model status: http://localhost:5000/api/debug/model-status
- Review logs for errors

## Next Steps

- Read [README.md](README.md) for detailed information
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues

## Need Help?

- Check logs for error messages
- Review troubleshooting guide
- Open an issue on GitHub

## Production Checklist

Before deploying to production:

- [ ] Change default secret keys
- [ ] Update MongoDB credentials
- [ ] Configure HTTPS/SSL
- [ ] Set up proper authentication
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test with real model files
- [ ] Optimize performance settings

## Useful Commands

```bash
# Check backend health
curl http://localhost:5000/health

# Check model status
curl http://localhost:5000/api/debug/model-status

# View backend logs (Docker)
docker-compose logs -f backend

# View frontend logs (Docker)
docker-compose logs -f frontend

# Restart services (Docker)
docker-compose restart

# Stop all services (Docker)
docker-compose down
```

Happy coding! 🚀
