# SmartAttendance - AI Face Recognition Attendance System

A production-ready fullstack attendance system with live face recognition, role-based access control, and real-time webcam streaming.

## Features

- **Live Face Recognition**: Real-time face detection and recognition from webcam stream
- **Role-Based Access**: Admin, Instructor, and Student dashboards
- **JWT Authentication**: Secure token-based authentication
- **MongoDB Integration**: Cloud-ready database with Atlas support
- **Docker Ready**: Complete containerization setup
- **Model Integration**: Support for pre-trained face recognition models

## Tech Stack

### Frontend
- React 18 + Vite + TypeScript
- TailwindCSS for styling
- Axios for API calls
- React Router for navigation

### Backend
- Python Flask REST API
- InsightFace/MTCNN for face detection
- ArcFace/FaceNet for embeddings
- JWT authentication
- MongoDB with PyMongo

### Database
- MongoDB (local or Atlas)
- Collections: users, students, attendance, sessions

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (local) or MongoDB Atlas account
- Docker & Docker Compose (optional)

### Setup

1. **Clone and install dependencies**

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

2. **Configure environment variables**

```bash
# Backend (.env in backend/)
cp .env.sample .env
# Edit with your MongoDB connection string

# Frontend (.env in frontend/)
cp .env.sample .env
```

3. **Train face recognition model**

```bash
# Quick training (recommended)
prepare_and_train.bat

# Or step by step:
# 1. Prepare dataset in backend/dataset/
# 2. Validate: cd backend && python prepare_dataset.py --validate
# 3. Train: python train_model.py
```

See [TRAINING_QUICK_START.md](TRAINING_QUICK_START.md) for detailed instructions.

4. **Run the application**

```bash
# Backend (from backend/)
python app.py

# Frontend (from frontend/)
npm run dev
```

### Docker Deployment

```bash
docker-compose up --build
```

## Project Structure

```
SmartAttendance/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # API client & utilities
│   │   └── types/           # TypeScript types
│   └── ...
├── backend/                 # Flask backend
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── blueprints/         # API routes
│   ├── recognizer/         # Face recognition pipeline
│   ├── db/                 # Database connection
│   ├── utils/              # Utilities
│   └── models/             # Trained models
└── docker-compose.yml      # Docker orchestration
```

## API Documentation

### Authentication
- `POST /api/auth/login` - Login (returns JWT + role)
- `POST /api/auth/register-student` - Register new student

### Admin
- `POST /api/admin/add-instructor` - Add instructor
- `GET /api/admin/instructors` - List instructors
- `GET /api/admin/attendance/all` - View all attendance
- `POST /api/admin/upload-model` - Upload model files

### Attendance
- `POST /api/attendance/recognize` - Recognize face from image
- `POST /api/attendance/start-session` - Start attendance session
- `POST /api/attendance/end-session` - End session
- `GET /api/attendance/student/{id}` - Get student attendance

### Debug
- `GET /api/debug/echo` - Test endpoint
- `POST /api/debug/recognition-test` - Test recognition without recording

## Face Recognition Model

### Training Your Own Model

The system uses a custom-trained face recognition model:

**Technology Stack:**
- **Face Detection**: MTCNN
- **Feature Extraction**: FaceNet (InceptionResnetV1 - VGGFace2)
- **Embeddings**: 512-dimensional vectors
- **Classification**: SVM or Logistic Regression
- **Open-Set Recognition**: Confidence threshold for unknown faces

**Quick Training:**
```bash
# 1. Organize dataset
backend/dataset/
├── STU001/
│   ├── photo1.jpg
│   └── photo2.jpg
└── STU002/
    └── ...

# 2. Train model
prepare_and_train.bat
```

**Model Files** (auto-generated in `backend/models/Classifier/`):
- `face_classifier.pkl` - Trained classifier
- `label_encoder.pkl` - Student ID encoder
- `model_metadata.pkl` - Configuration & threshold

**Recognition Pipeline:**
1. Face detection (MTCNN)
2. Face alignment & cropping (160x160)
3. Embedding generation (FaceNet → 512-dim)
4. Classification (SVM/LogisticRegression)
5. Confidence threshold check (open-set recognition)

See [TRAINING_GUIDE.md](TRAINING_GUIDE.md) for comprehensive training documentation.

## User Roles

### Admin
- Manage instructors and students
- Upload/manage models
- View and export all attendance records

### Instructor
- Start/end attendance sessions
- Use live webcam stream for recognition
- View session attendance
- One record per student per session

### Student
- View personal attendance history
- Register face images

## Troubleshooting

### Model not loading
- Ensure all model files are in `backend/models/Classifier/`
- Check file permissions
- Verify pickle compatibility (Python 3.9+)

### Camera not working
- Grant browser camera permissions
- Use HTTPS in production
- Check browser compatibility

### MongoDB connection issues
- Verify connection string in .env
- Check network access in MongoDB Atlas
- Ensure IP whitelist is configured

## MongoDB Connection

Default connection string (update in backend/.env):
```
MONGODB_URI=mongodb+srv://bekamayela18_db_user:2qBIVM2Qn3IZDAQy@cluster0.ifaywcg.mongodb.net/
```

## License

MIT
