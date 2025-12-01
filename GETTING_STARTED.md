# Getting Started with SmartAttendance

Welcome to SmartAttendance! This guide will help you get the system up and running.

## What You Have

A complete, production-ready AI-powered face recognition attendance system with:

✅ **Backend (Flask + Python)**
- REST API with JWT authentication
- Face recognition pipeline (detection → embedding → classification)
- MongoDB integration
- Role-based access control (Admin, Instructor, Student)
- Support for your existing trained models

✅ **Frontend (React + TypeScript + Vite)**
- Modern, responsive UI with TailwindCSS
- Live camera streaming with auto-capture
- Role-specific dashboards
- Real-time attendance tracking

✅ **Docker Support**
- Complete containerization
- One-command deployment

✅ **Documentation**
- API documentation
- Deployment guides
- Troubleshooting guides
- Testing guides

## Your Model Files

The system is designed to work with your existing model structure:
```
backend/models/Classifier/
├── face_classifier_v1.pkl          # Your trained classifier
├── classifier.pkl                   # Optional alternative
├── label_encoder.pkl               # Your label encoder
├── label_encoder_classes.npy       # Class labels
├── labels.csv                      # Optional label mapping
├── X.npy                           # Optional training features
└── y.npy                           # Optional training labels
```

**Important:** Place your model files in this directory before running the system.

## Quick Setup (5 Minutes)

### 1. Install Prerequisites

**Required:**
- Python 3.9+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))
- Git

**Optional:**
- Docker & Docker Compose (for containerized deployment)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd SmartAttendance

# Run automated setup (Linux/Mac)
chmod +x setup.sh
./setup.sh
```

Or manually:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.sample .env
```

### 3. Configure Environment

**Backend** (`backend/.env`):
```env
# Your MongoDB connection string is already configured
MONGODB_URI=mongodb+srv://bekamayela18_db_user:2qBIVM2Qn3IZDAQy@cluster0.ifaywcg.mongodb.net/
MONGODB_DB_NAME=smart_attendance

# Change these in production
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-change-this

# Recognition settings
RECOGNITION_THRESHOLD=0.60
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://127.0.0.1:5000
```

### 4. Add Your Model Files

Copy your trained model files to `backend/models/Classifier/`:
```bash
cp /path/to/your/face_classifier_v1.pkl backend/models/Classifier/
cp /path/to/your/label_encoder.pkl backend/models/Classifier/
cp /path/to/your/label_encoder_classes.npy backend/models/Classifier/
```

### 5. Initialize Database

```bash
cd backend
python seed_db.py
```

This creates demo accounts:
- **Admin:** `admin` / `admin123`
- **Instructor:** `instructor` / `inst123`
- **Student:** `student` / `stud123`

### 6. Run the Application

**Option A: Development Mode**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Access: http://localhost:5173

**Option B: Docker**

```bash
docker-compose up --build
```

Access: http://localhost

## First Steps

### 1. Test the System

1. Open http://localhost:5173
2. Login as admin: `admin` / `admin123`
3. Explore the dashboard
4. Check system statistics

### 2. Verify Model Loading

```bash
curl http://localhost:5000/api/debug/model-status
```

Should show:
```json
{
  "model_loaded": true,
  "files": {
    "classifier": true,
    "label_encoder": true,
    "label_classes": true
  }
}
```

### 3. Test Recognition

```bash
curl -X POST -F "image=@test_face.jpg" \
  http://localhost:5000/api/debug/recognition-test
```

### 4. Try Live Attendance

1. Login as instructor: `instructor` / `inst123`
2. Click "Start New Session"
3. Enter session details
4. Click "Create & Start"
5. Allow camera access
6. System will automatically capture and recognize faces
7. Watch attendance list update in real-time

## System Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │────────▶│   React     │────────▶│   Flask     │
│  (Camera)   │  HTTP   │  Frontend   │   API   │   Backend   │
└─────────────┘         └─────────────┘         └─────────────┘
                                                        │
                                                        ▼
                                                 ┌─────────────┐
                                                 │  MongoDB    │
                                                 │   Atlas     │
                                                 └─────────────┘
                                                        │
                                                        ▼
                                                 ┌─────────────┐
                                                 │   Models    │
                                                 │  Classifier │
                                                 └─────────────┘
```

## User Roles

### Admin
- Manage instructors and students
- View system statistics
- Access all attendance records
- Upload/manage model files

### Instructor
- Start/end attendance sessions
- Use live camera for face recognition
- View session attendance
- One record per student per session

### Student
- View personal attendance history
- Register face images
- Check attendance statistics

## Recognition Pipeline

```
Camera Frame → Face Detection → Face Alignment → 
Embedding Generation → Classification → 
Confidence Check → Database Lookup → 
Attendance Recording → Result Display
```

**Key Features:**
- Automatic face detection
- Real-time recognition
- Confidence threshold filtering (default: 60%)
- Duplicate prevention (one record per session)
- Unknown student handling

## Project Structure

```
SmartAttendance/
├── backend/              # Flask API
│   ├── app.py           # Main application
│   ├── blueprints/      # API routes
│   ├── recognizer/      # Face recognition
│   ├── db/              # Database
│   └── models/          # Your trained models
│
├── frontend/            # React UI
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable components
│   │   └── lib/        # API client
│   └── ...
│
└── Documentation/       # Guides
```

## Common Tasks

### Add a New Instructor (as Admin)
1. Login as admin
2. Click "Add Instructor"
3. Fill in details
4. Submit

### Register Student Face
1. Login as student
2. Click "Register Face"
3. Capture 5-10 images from different angles
4. Submit

### Take Attendance (as Instructor)
1. Login as instructor
2. Start new session
3. Camera auto-captures frames
4. System recognizes students automatically
5. View attendance list in real-time
6. End session when done

### View Attendance (as Student)
1. Login as student
2. View attendance history table
3. Check statistics

## Customization

### Adjust Recognition Threshold

Edit `backend/.env`:
```env
RECOGNITION_THRESHOLD=0.50  # Lower = more lenient
RECOGNITION_THRESHOLD=0.80  # Higher = more strict
```

### Change Capture Interval

Edit `frontend/src/pages/AttendanceSession.tsx`:
```typescript
<CameraPreview 
  autoCapture={true}
  captureInterval={3000}  // 3 seconds
/>
```

### Modify UI Theme

Edit `frontend/tailwind.config.js` to customize colors and styles.

## Troubleshooting

### Backend won't start
```bash
# Check MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('your-uri'); print(client.server_info())"

# Check port availability
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows
```

### Model not loading
```bash
# Verify files exist
ls -la backend/models/Classifier/

# Check model status
curl http://localhost:5000/api/debug/model-status

# Force reload
curl -X POST http://localhost:5000/api/debug/reload-models
```

### Camera not working
- Grant browser camera permissions
- Use HTTPS in production
- Try different browser
- Check if camera is in use

### Recognition not accurate
- Adjust threshold in .env
- Ensure good lighting
- Register more face images
- Retrain model with more data

## Next Steps

1. **Read Documentation:**
   - [README.md](README.md) - Overview
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

2. **Customize:**
   - Update branding and colors
   - Add your logo
   - Modify email templates
   - Configure notifications

3. **Deploy:**
   - Set up production environment
   - Configure HTTPS/SSL
   - Set up monitoring
   - Configure backups

4. **Extend:**
   - Add more features
   - Integrate with existing systems
   - Add reporting capabilities
   - Implement analytics

## Support

- **Documentation:** Check the docs/ folder
- **Issues:** Create GitHub issue
- **Email:** your-email@example.com

## Security Checklist

Before going to production:

- [ ] Change default SECRET_KEY
- [ ] Change default JWT_SECRET_KEY
- [ ] Update MongoDB credentials
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up rate limiting
- [ ] Enable logging
- [ ] Configure backups
- [ ] Review CORS settings
- [ ] Test security vulnerabilities

## Performance Tips

- Use GPU for faster recognition (if available)
- Optimize image sizes
- Enable caching
- Use CDN for static assets
- Monitor resource usage
- Scale horizontally as needed

## License

MIT License - Feel free to use and modify

---

**Ready to go!** 🚀

Start with the Quick Setup above, then explore the system. The demo accounts will let you test all features immediately.

For detailed information, check the other documentation files in this repository.

Happy coding!
