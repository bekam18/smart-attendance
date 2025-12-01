# SmartAttendance - Quick Reference Card

## 🚀 Quick Commands

### Setup
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### Run Development
```bash
# Backend (Terminal 1)
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python app.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Run Docker
```bash
docker-compose up --build
```

### Seed Database
```bash
cd backend
python seed_db.py
```

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Instructor | instructor | inst123 |
| Student | student | stud123 |

## 🌐 URLs

| Service | Development | Docker |
|---------|-------------|--------|
| Frontend | http://localhost:5173 | http://localhost |
| Backend | http://localhost:5000 | http://localhost:5000 |
| Health | http://localhost:5000/health | http://localhost:5000/health |

## 📁 Important Paths

```
backend/models/Classifier/    # Place your model files here
backend/uploads/              # Uploaded face images
backend/.env                  # Backend configuration
frontend/.env                 # Frontend configuration
```

## 🔧 Configuration

### Backend (.env)
```env
MONGODB_URI=mongodb+srv://...
SECRET_KEY=change-in-production
JWT_SECRET_KEY=change-in-production
RECOGNITION_THRESHOLD=0.60
FLASK_PORT=5000
```

### Frontend (.env)
```env
VITE_API_URL=http://127.0.0.1:5000
```

## 📊 Model Files Required

```
backend/models/Classifier/
├── face_classifier_v1.pkl          ✅ Required
├── label_encoder.pkl               ✅ Required
└── label_encoder_classes.npy       ✅ Required
```

## 🔍 Debug Endpoints

```bash
# Check health
curl http://localhost:5000/health

# Check model status
curl http://localhost:5000/api/debug/model-status

# Test recognition
curl -X POST -F "image=@face.jpg" \
  http://localhost:5000/api/debug/recognition-test

# Reload models
curl -X POST http://localhost:5000/api/debug/reload-models
```

## 🎯 Common Tasks

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Start Session (Instructor)
```bash
curl -X POST http://localhost:5000/api/attendance/start-session \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Morning Class","course":"CS101"}'
```

### Recognize Face
```bash
curl -X POST http://localhost:5000/api/attendance/recognize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@face.jpg" \
  -F "session_id=SESSION_ID"
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('your-uri'); print('Connected')"

# Check port
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Linux/Mac
```

### Frontend won't start
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Model not loading
```bash
# Check files exist
dir backend\models\Classifier  # Windows
ls -la backend/models/Classifier/  # Linux/Mac

# Check status
curl http://localhost:5000/api/debug/model-status
```

### Camera not working
- Grant browser permissions
- Use HTTPS in production
- Try different browser

## 📦 Dependencies

### Install Backend
```bash
cd backend
pip install -r requirements.txt
```

### Install Frontend
```bash
cd frontend
npm install
```

## 🔐 Security Checklist

- [ ] Change SECRET_KEY
- [ ] Change JWT_SECRET_KEY
- [ ] Update MongoDB credentials
- [ ] Enable HTTPS
- [ ] Configure CORS
- [ ] Set up rate limiting

## 📱 Browser Support

✅ Chrome, Firefox, Safari, Edge (latest)
✅ Mobile Chrome, Mobile Safari

## 🎨 User Roles

### Admin
- Manage users
- View all data
- System statistics
- Upload models

### Instructor
- Create sessions
- Live recognition
- View attendance
- Manage sessions

### Student
- View attendance
- Register face
- Check statistics

## 🔄 Recognition Flow

```
Camera → Detect → Align → Embed → 
Classify → Check → Record → Display
```

## 📈 Performance

- Recognition: < 2s per frame
- Auto-capture: Every 2s (configurable)
- Threshold: 0.60 (60% confidence)
- Duplicate: Prevented per session

## 🌐 API Endpoints

### Auth
- POST /api/auth/login
- POST /api/auth/register-student
- GET /api/auth/me

### Admin
- POST /api/admin/add-instructor
- GET /api/admin/instructors
- GET /api/admin/students
- GET /api/admin/attendance/all
- GET /api/admin/stats

### Attendance
- POST /api/attendance/start-session
- POST /api/attendance/end-session
- POST /api/attendance/recognize
- GET /api/attendance/sessions

### Students
- GET /api/students/profile
- POST /api/students/register-face
- GET /api/students/attendance

## 🔧 Useful Commands

```bash
# View logs (Docker)
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services (Docker)
docker-compose restart

# Stop services (Docker)
docker-compose down

# Build frontend
cd frontend && npm run build

# Run tests
cd backend && pytest
cd frontend && npm test
```

## 📚 Documentation Files

1. README.md - Overview
2. GETTING_STARTED.md - Setup guide
3. QUICKSTART.md - 5-minute guide
4. API_DOCUMENTATION.md - API reference
5. DEPLOYMENT.md - Production guide
6. TROUBLESHOOTING.md - Common issues
7. TESTING.md - Testing guide
8. PROJECT_STRUCTURE.md - Architecture
9. PROJECT_SUMMARY.md - Complete summary
10. QUICK_REFERENCE.md - This file

## 💡 Tips

1. Start with demo accounts
2. Test with debug endpoints
3. Ensure good lighting
4. Register multiple face images
5. Adjust threshold as needed
6. Monitor logs for issues
7. Read documentation
8. Change defaults in production

## 🎯 Next Steps

1. ✅ Run setup script
2. ✅ Add model files
3. ✅ Seed database
4. ✅ Start services
5. ✅ Login and test
6. ✅ Customize as needed
7. ✅ Deploy to production

## 📞 Support

- Check documentation
- Review troubleshooting guide
- Test with debug endpoints
- Check logs for errors

## ⚡ Quick Test

```bash
# 1. Check backend
curl http://localhost:5000/health

# 2. Check models
curl http://localhost:5000/api/debug/model-status

# 3. Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 4. Open frontend
# Navigate to http://localhost:5173
```

## 🎉 You're Ready!

Everything is set up and ready to use. Just follow the Quick Commands above to get started!

---

**SmartAttendance** - AI-Powered Face Recognition Attendance System
