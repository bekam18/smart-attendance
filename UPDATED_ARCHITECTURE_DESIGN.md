# 5.2 Architecture Design

The Smart Attendance System follows a three-tier client-server architecture with clear separation between presentation, application logic, and data management layers. This modular design enables independent development, testing, and maintenance of each component while ensuring scalability and security.

## Architectural Layers

### 1. Presentation Layer (Frontend)
- **Technology:** React with TypeScript
- **Components:** User interfaces for Admin, Instructor, and Student dashboards
- **Functions:** Session management, real-time attendance display, report generation
- **Communication:** RESTful API calls to backend via HTTP/HTTPS

### 2. Application Layer (Backend)
- **Technology:** Flask (Python)
- **Components:** 
  - Authentication module (JWT-based)
  - Face recognition engine (InsightFace/OpenCV)
  - Session management logic
  - Report generation service
- **Functions:** Business logic, data validation, security enforcement
- **Communication:** Processes requests from frontend, queries database

### 3. Data Layer (Database)
- **Technology:** MySQL
- **Components:** Users, Students, Sessions, Attendance tables
- **Functions:** Persistent storage, data retrieval, transaction management
- **Security:** Encrypted passwords (bcrypt), parameterized queries

## System Workflow

The attendance recording process follows these steps:

1. **Image Acquisition:** Webcam captures live video frames via browser MediaStream API
2. **Face Detection:** InsightFace detector identifies faces in captured images
3. **Feature Extraction:** System generates facial embeddings (128-dimensional vectors)
4. **Recognition:** Embeddings compared with stored student data using similarity matching
5. **Validation:** System verifies student belongs to session's section and year
6. **Attendance Logging:** Record created in database with timestamp and confidence score
7. **UI Update:** Real-time attendance list refreshed to show marked students
8. **Data Storage:** Attendance records stored permanently in MySQL database

## Key Architectural Features

### Modularity
- Independent frontend and backend deployment
- Separate authentication, recognition, and reporting modules
- Blueprint-based routing for organized code structure

### Scalability
- Supports multiple concurrent sessions (tested with 5 simultaneous sessions)
- Database indexing for efficient queries with large datasets
- Connection pooling for handling concurrent requests

### Security
- JWT token-based authentication with 24-hour expiration
- Role-based access control (Admin, Instructor, Student)
- SQL injection protection through parameterized queries
- Password hashing with bcrypt (12 rounds)

### Reusability
- Facial embeddings stored once, used for all recognition attempts
- Model retraining supported without system downtime
- Shared authentication module across all user roles

### Integration
- RESTful API design for easy third-party integration
- CSV/Excel export for compatibility with external tools
- Email service integration for password reset functionality

## Architectural Goals Achieved

✅ **Reusability:** Facial embeddings stored permanently, eliminating need for repeated training  
✅ **Integration:** Report export in standard formats (CSV/Excel) for external analysis  
✅ **Scalability:** Multi-session support with database optimization for growth  
✅ **Security:** Multi-layer protection with encryption, authentication, and access control  
✅ **Maintainability:** Modular design allows independent component updates  
✅ **Performance:** 1-3 second recognition time with real-time UI updates

This architecture ensures the system is robust, secure, and capable of meeting current requirements while supporting future enhancements and scaling needs.
