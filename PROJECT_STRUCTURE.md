# Project Structure

Complete overview of the SmartAttendance project structure.

```
SmartAttendance/
│
├── backend/                          # Flask Backend
│   ├── app.py                       # Main application entry point
│   ├── config.py                    # Configuration management
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend Docker configuration
│   ├── .env.sample                  # Environment variables template
│   ├── seed_db.py                   # Database seeding script
│   │
│   ├── blueprints/                  # API route blueprints
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── admin.py                # Admin management endpoints
│   │   ├── students.py             # Student endpoints
│   │   ├── attendance.py           # Attendance management endpoints
│   │   └── debug.py                # Debug and testing endpoints
│   │
│   ├── recognizer/                  # Face recognition pipeline
│   │   ├── loader.py               # Model loading and management
│   │   ├── detector.py             # Face detection (OpenCV/MTCNN/InsightFace)
│   │   ├── embeddings.py           # Face embedding generation
│   │   └── classifier.py           # Face classification and recognition
│   │
│   ├── db/                          # Database layer
│   │   └── mongo.py                # MongoDB connection and initialization
│   │
│   ├── utils/                       # Utility functions
│   │   ├── security.py             # Password hashing, JWT, role checking
│   │   └── image_tools.py          # Image processing utilities
│   │
│   ├── models/                      # Trained model files
│   │   └── Classifier/
│   │       ├── .gitkeep
│   │       ├── face_classifier_v1.pkl      # Trained classifier
│   │       ├── label_encoder.pkl           # Label encoder
│   │       ├── label_encoder_classes.npy   # Class labels
│   │       ├── labels.csv                  # Optional: label mapping
│   │       ├── X.npy                       # Optional: training features
│   │       └── y.npy                       # Optional: training labels
│   │
│   └── uploads/                     # User uploaded files
│       ├── .gitkeep
│       └── faces/                   # Student face images
│           └── {student_id}/        # Per-student directories
│
├── frontend/                         # React Frontend
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.ts              # Vite configuration
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tailwind.config.js          # TailwindCSS configuration
│   ├── postcss.config.js           # PostCSS configuration
│   ├── Dockerfile                   # Frontend Docker configuration
│   ├── nginx.conf                   # Nginx configuration for production
│   ├── .env.sample                  # Environment variables template
│   │
│   ├── src/
│   │   ├── main.tsx                # Application entry point
│   │   ├── App.tsx                 # Main App component with routing
│   │   ├── index.css               # Global styles
│   │   │
│   │   ├── components/             # Reusable components
│   │   │   ├── Layout.tsx          # Main layout wrapper
│   │   │   └── CameraPreview.tsx   # Camera component with live capture
│   │   │
│   │   ├── pages/                  # Page components
│   │   │   ├── Login.tsx           # Login page (all roles)
│   │   │   ├── AdminDashboard.tsx  # Admin dashboard
│   │   │   ├── InstructorDashboard.tsx  # Instructor dashboard
│   │   │   ├── StudentDashboard.tsx     # Student dashboard
│   │   │   ├── AttendanceSession.tsx    # Live attendance session
│   │   │   └── StudentRegistration.tsx  # Face registration
│   │   │
│   │   ├── lib/                    # Utilities and API
│   │   │   ├── api.ts              # API client with axios
│   │   │   └── auth.ts             # Authentication utilities
│   │   │
│   │   └── types/                  # TypeScript type definitions
│   │       └── index.ts            # Shared types and interfaces
│   │
│   └── public/                      # Static assets
│
├── docker-compose.yml               # Docker Compose configuration
├── .gitignore                       # Git ignore rules
├── setup.sh                         # Setup script
│
└── Documentation/
    ├── README.md                    # Main documentation
    ├── QUICKSTART.md               # Quick start guide
    ├── API_DOCUMENTATION.md        # API reference
    ├── DEPLOYMENT.md               # Deployment guide
    ├── TROUBLESHOOTING.md          # Troubleshooting guide
    └── PROJECT_STRUCTURE.md        # This file

```

## Key Components

### Backend Architecture

#### 1. Application Layer (`app.py`)
- Flask application initialization
- Blueprint registration
- CORS configuration
- JWT setup
- Error handlers

#### 2. API Blueprints (`blueprints/`)
- **auth.py**: User authentication and registration
- **admin.py**: Admin operations (manage users, view stats)
- **students.py**: Student profile and face registration
- **attendance.py**: Attendance sessions and recognition
- **debug.py**: Testing and debugging endpoints

#### 3. Recognition Pipeline (`recognizer/`)
- **loader.py**: Load and manage trained models
- **detector.py**: Detect faces in images (multiple methods)
- **embeddings.py**: Generate face embeddings
- **classifier.py**: Classify faces and return results

#### 4. Database Layer (`db/`)
- MongoDB connection management
- Index creation
- Database initialization

#### 5. Utilities (`utils/`)
- **security.py**: Password hashing, JWT, role-based access
- **image_tools.py**: Image encoding/decoding, resizing

### Frontend Architecture

#### 1. Routing (`App.tsx`)
- Protected routes with role-based access
- Automatic redirection based on user role
- Route guards for authentication

#### 2. Components (`components/`)
- **Layout**: Consistent page layout with navigation
- **CameraPreview**: Live camera feed with auto-capture

#### 3. Pages (`pages/`)
- **Login**: Universal login for all roles
- **AdminDashboard**: System statistics, user management
- **InstructorDashboard**: Session management
- **AttendanceSession**: Live recognition interface
- **StudentDashboard**: Personal attendance history
- **StudentRegistration**: Face image capture/upload

#### 4. API Layer (`lib/`)
- Centralized API client with axios
- Automatic token injection
- Error handling and redirects

#### 5. Types (`types/`)
- TypeScript interfaces for type safety
- Shared data models

## Data Flow

### Authentication Flow
```
User → Login Page → POST /api/auth/login → JWT Token → Store in localStorage → Redirect to Dashboard
```

### Recognition Flow
```
Camera → Capture Frame → POST /api/attendance/recognize → 
Face Detection → Embedding Generation → Classification → 
Database Check → Record Attendance → Return Result
```

### Session Flow
```
Instructor → Start Session → POST /api/attendance/start-session →
Create Session Record → Open Camera → Auto-capture Frames →
Recognize Faces → Record Attendance → End Session
```

## Database Schema

### Collections

#### users
```javascript
{
  _id: ObjectId,
  username: String (unique),
  password: String (hashed),
  email: String (unique),
  name: String,
  role: String (admin|instructor|student),
  department: String (optional),
  created_at: DateTime
}
```

#### students
```javascript
{
  _id: ObjectId,
  user_id: String (ref: users._id),
  student_id: String (unique),
  name: String,
  email: String,
  department: String,
  year: String,
  face_registered: Boolean,
  face_images_count: Number,
  last_face_update: DateTime,
  created_at: DateTime
}
```

#### attendance
```javascript
{
  _id: ObjectId,
  student_id: String (ref: students.student_id),
  session_id: String (ref: sessions._id),
  timestamp: DateTime,
  date: String (YYYY-MM-DD),
  confidence: Number,
  status: String (present)
}
```

#### sessions
```javascript
{
  _id: ObjectId,
  instructor_id: String (ref: users._id),
  instructor_name: String,
  name: String,
  course: String,
  start_time: DateTime,
  end_time: DateTime (nullable),
  status: String (active|completed),
  attendance_count: Number
}
```

## Environment Variables

### Backend
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name
- `RECOGNITION_THRESHOLD`: Confidence threshold (0.0-1.0)
- `FLASK_HOST`: Server host
- `FLASK_PORT`: Server port
- `CORS_ORIGINS`: Allowed CORS origins

### Frontend
- `VITE_API_URL`: Backend API URL

## Security Features

1. **Password Hashing**: bcrypt with salt
2. **JWT Authentication**: Secure token-based auth
3. **Role-Based Access Control**: Decorator-based permissions
4. **CORS Protection**: Configurable allowed origins
5. **Input Validation**: Request data validation
6. **SQL Injection Prevention**: MongoDB parameterized queries

## Performance Considerations

1. **Database Indexes**: Optimized queries with indexes
2. **Image Optimization**: Resize images before processing
3. **Lazy Loading**: Frontend code splitting
4. **Caching**: Model loaded once and reused
5. **Async Operations**: Non-blocking I/O

## Scalability

1. **Horizontal Scaling**: Stateless backend design
2. **Load Balancing**: Multiple backend instances
3. **Database Sharding**: MongoDB Atlas auto-scaling
4. **CDN**: Static asset delivery
5. **Microservices**: Recognition can be separated

## Testing Strategy

1. **Unit Tests**: Individual function testing
2. **Integration Tests**: API endpoint testing
3. **E2E Tests**: Full user flow testing
4. **Load Tests**: Performance under load
5. **Security Tests**: Vulnerability scanning

## Deployment Options

1. **Docker Compose**: Local/development deployment
2. **AWS**: EC2, ECS, or Elastic Beanstalk
3. **Heroku**: Quick cloud deployment
4. **DigitalOcean**: Droplet deployment
5. **Kubernetes**: Enterprise-scale deployment

## Monitoring and Logging

1. **Application Logs**: Flask logging
2. **Access Logs**: Nginx access logs
3. **Error Tracking**: Sentry integration (optional)
4. **Performance Monitoring**: New Relic (optional)
5. **Database Monitoring**: MongoDB Atlas monitoring

## Future Enhancements

1. **WebSocket Support**: Real-time updates
2. **Mobile App**: React Native version
3. **Advanced Analytics**: Attendance insights
4. **Email Notifications**: Automated alerts
5. **Multi-language Support**: i18n
6. **Biometric Integration**: Fingerprint, iris scan
7. **Offline Mode**: PWA capabilities
8. **Report Generation**: PDF/Excel exports
9. **API Rate Limiting**: Request throttling
10. **Audit Logs**: User action tracking
