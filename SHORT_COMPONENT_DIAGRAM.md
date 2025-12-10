# 5.2.1 Component Diagram

The component diagram shows the modular structure of the Smart Attendance System and how components interact to deliver complete functionality.

## Core Components

**1. Frontend (React)** - User interfaces for Admin, Instructor, and Student dashboards  
**2. Camera Module** - Captures live video frames via browser webcam  
**3. Face Detection** - Locates faces using InsightFace/OpenCV  
**4. Face Recognition** - Identifies students from facial embeddings  
**5. Authentication** - Manages login and access control (JWT, bcrypt)  
**6. Session Management** - Controls attendance session lifecycle  
**7. Attendance Logger** - Records attendance with duplicate prevention  
**8. Database (MySQL)** - Stores users, students, sessions, and attendance  
**9. Report Generator** - Creates CSV/Excel reports with filters  
**10. Email Service** - Sends password reset notifications  

## Component Interaction Flow

```
User Interface (React) → Camera Module → Face Detection → 
Face Recognition → Attendance Logger → Database (MySQL)
                ↓
        Report Generator → CSV/Excel Export
```

## Key Features

- **Modular Design:** Independent components with clear responsibilities
- **Loose Coupling:** Components interact through well-defined interfaces
- **Reusability:** Facial embeddings stored once, used repeatedly
- **Scalability:** Supports multiple concurrent sessions
- **Security:** JWT authentication, encrypted passwords, SQL injection protection

This architecture ensures maintainability, testability, and ease of future enhancements.
