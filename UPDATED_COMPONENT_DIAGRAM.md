# 5.2.1 Component Diagram

The component diagram illustrates the modular structure of the Smart Attendance System, showing how different components interact to deliver the complete functionality. Each component has a specific responsibility and communicates with other components through well-defined interfaces.

## System Components

### 1. Frontend Layer (React)
**Purpose:** User interface for all actors  
**Components:**
- Admin Dashboard (user management, system reports)
- Instructor Dashboard (session management, attendance recording)
- Student Dashboard (attendance history, statistics)
- Authentication Pages (login, password reset)

**Technology:** React with TypeScript, Vite build system

---

### 2. Camera Module
**Purpose:** Captures live video frames for face recognition  
**Function:** Accesses webcam via browser MediaStream API, captures images every 2 seconds  
**Output:** JPEG/PNG images sent to backend for processing

---

### 3. Face Detection Module
**Purpose:** Locates faces in captured images  
**Technology:** InsightFace detector with OpenCV fallback  
**Function:** Identifies face regions and extracts bounding boxes  
**Output:** Face coordinates and cropped face images

---

### 4. Face Recognition Module
**Purpose:** Identifies students from facial features  
**Technology:** Pre-trained face recognition model  
**Function:** 
- Extracts 128-dimensional facial embeddings
- Compares embeddings with stored student data
- Calculates similarity scores (confidence)
**Output:** Student ID and confidence score (0-100%)

---

### 5. Authentication Module
**Purpose:** Manages user login and access control  
**Technology:** JWT (JSON Web Tokens), bcrypt password hashing  
**Function:**
- Validates user credentials
- Issues authentication tokens
- Enforces role-based permissions
**Output:** Secure access tokens with 24-hour expiration

---

### 6. Session Management Module
**Purpose:** Controls attendance session lifecycle  
**Function:**
- Creates new sessions with course/section details
- Manages session states (active, stopped_daily, ended_semester)
- Implements 12-hour retake feature
- Handles session reopening logic
**Output:** Session data and status updates

---

### 7. Attendance Logger
**Purpose:** Records and manages attendance data  
**Function:**
- Creates attendance records with timestamps
- Prevents duplicate entries within active sessions
- Marks absent students when camera stopped
- Validates section/year matching
**Output:** Attendance records stored in database

---

### 8. Database Layer (MySQL)
**Purpose:** Persistent data storage  
**Tables:**
- Users (authentication credentials)
- Students (profile information)
- Sessions (attendance session details)
- Attendance (attendance records)

**Features:** Indexed queries, foreign key constraints, transaction support

---

### 9. Report Generator
**Purpose:** Creates attendance reports with filtering options  
**Function:**
- Queries attendance data with date/course filters
- Calculates statistics (present/absent counts, percentages)
- Formats data for export
**Output:** CSV and Excel (.xlsx) files

---

### 10. Email Service
**Purpose:** Sends password reset emails  
**Technology:** SMTP with support for Gmail, Outlook, SendGrid  
**Function:** Generates secure reset tokens, sends HTML-formatted emails  
**Output:** Email notifications with reset links

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Admin     │  │  Instructor  │  │   Student    │         │
│  │  Dashboard   │  │  Dashboard   │  │  Dashboard   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼────────┐                          │
│                    │  Camera Module │                          │
│                    └───────┬────────┘                          │
└────────────────────────────┼───────────────────────────────────┘
                             │ HTTP/REST API
┌────────────────────────────▼───────────────────────────────────┐
│                      BACKEND (Flask)                            │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐ │
│  │ Authentication│◄────►│   Session    │◄────►│  Attendance │ │
│  │    Module     │      │  Management  │      │   Logger    │ │
│  └──────────────┘      └──────────────┘      └─────────────┘ │
│         │                                            │         │
│         │              ┌──────────────┐              │         │
│         └─────────────►│     Face     │◄─────────────┘         │
│                        │  Detection   │                        │
│                        └──────┬───────┘                        │
│                               │                                │
│                        ┌──────▼───────┐                        │
│                        │     Face     │                        │
│                        │ Recognition  │                        │
│                        └──────┬───────┘                        │
│                               │                                │
│  ┌──────────────┐      ┌─────▼────────┐      ┌─────────────┐ │
│  │    Report    │◄────►│   Database   │◄────►│    Email    │ │
│  │  Generator   │      │    Layer     │      │   Service   │ │
│  └──────────────┘      └──────────────┘      └─────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MySQL Database │
                    │  (Data Storage) │
                    └─────────────────┘
```

## Component Dependencies

| Component | Depends On | Provides To |
|-----------|------------|-------------|
| Frontend | Backend API | User interface |
| Camera Module | Browser API | Face images |
| Face Detection | Camera Module | Face coordinates |
| Face Recognition | Face Detection | Student identification |
| Authentication | Database | Access tokens |
| Session Management | Database, Authentication | Session control |
| Attendance Logger | Face Recognition, Database | Attendance records |
| Report Generator | Database | Export files |
| Email Service | SMTP Server | Notifications |
| Database | MySQL Server | Data persistence |

## Key Design Principles

**Separation of Concerns:** Each component has a single, well-defined responsibility  
**Loose Coupling:** Components interact through interfaces, not direct dependencies  
**High Cohesion:** Related functions grouped within same component  
**Reusability:** Components can be used across different parts of the system  
**Testability:** Each component can be tested independently

This modular architecture ensures maintainability, scalability, and ease of future enhancements.
