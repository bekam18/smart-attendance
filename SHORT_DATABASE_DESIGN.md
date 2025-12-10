# 5.3 Database Design

The database design ensures efficient storage, retrieval, and integrity of user information and attendance records. The Smart Attendance System uses MySQL as its relational database management system, providing robust support for concurrent access, data integrity, and scalability.

## Design Principles

**Normalization:** Eliminates data redundancy through proper table structure  
**Referential Integrity:** Foreign key constraints maintain data consistency  
**Indexing:** Optimizes query performance for large datasets  
**Security:** Encrypted passwords and parameterized queries prevent SQL injection

## Core Database Tables

### 1. Users Table
Stores authentication credentials for all system users (Admin, Instructor, Student)

**Attributes:**
- `id` (PK) - Unique user identifier
- `username` - Login username (unique)
- `password` - Hashed password (bcrypt)
- `email` - User email address (unique)
- `role` - User role (admin, instructor, student)
- `name` - Full name

### 2. Students Table
Stores student profile information

**Attributes:**
- `id` (PK) - Auto-increment identifier
- `user_id` (FK) - Links to Users table
- `student_id` - Student ID number (unique)
- `name` - Student full name
- `email` - Student email
- `department` - Academic department
- `year` - Academic year (1, 2, 3, 4)
- `section` - Class section (A, B, C, D)
- `face_registered` - Boolean flag for face enrollment

### 3. Sessions Table
Stores attendance session information

**Attributes:**
- `id` (PK) - Session identifier
- `instructor_id` (FK) - Links to Users table
- `instructor_name` - Instructor name
- `section_id` - Class section
- `year` - Academic year
- `session_type` - Lab or Theory
- `time_block` - Morning or Afternoon
- `course_name` - Course name
- `name` - Session name
- `start_time` - Session start timestamp
- `end_time` - Session end timestamp
- `status` - Session status (active, stopped_daily, ended_semester)
- `attendance_count` - Number of students marked

### 4. Attendance Table
Stores attendance records

**Attributes:**
- `id` (PK) - Record identifier
- `student_id` (FK) - Links to Students table
- `session_id` (FK) - Links to Sessions table
- `instructor_id` (FK) - Links to Users table
- `section_id` - Class section
- `year` - Academic year
- `session_type` - Lab or Theory
- `time_block` - Morning or Afternoon
- `course_name` - Course name
- `timestamp` - Record creation time
- `date` - Attendance date
- `confidence` - Recognition confidence (0.0-1.0)
- `status` - Present or Absent

## 5.3.1 Entity Relationship Diagram (ERD)

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    Users    │         │   Students   │         │  Sessions   │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ id (PK)     │◄───────┤│ user_id (FK) │         │ id (PK)     │
│ username    │         │ student_id   │         │ instructor  │
│ password    │         │ name         │         │ section_id  │
│ email       │         │ section      │         │ year        │
│ role        │         │ year         │         │ status      │
│ name        │         └──────┬───────┘         └──────┬──────┘
└──────┬──────┘                │                        │
       │                       │                        │
       │                       │    ┌───────────────────┘
       │                       │    │
       │                       ▼    ▼
       │                ┌──────────────┐
       └───────────────►│  Attendance  │
                        ├──────────────┤
                        │ id (PK)      │
                        │ student_id   │◄─── FK to Students
                        │ session_id   │◄─── FK to Sessions
                        │ instructor_id│◄─── FK to Users
                        │ timestamp    │
                        │ date         │
                        │ confidence   │
                        │ status       │
                        └──────────────┘
```

## Key Relationships

**Users → Students:** One-to-One (Each student has one user account)  
**Users → Sessions:** One-to-Many (Instructor creates multiple sessions)  
**Sessions → Attendance:** One-to-Many (Session has multiple attendance records)  
**Students → Attendance:** One-to-Many (Student has multiple attendance records)

## Database Constraints

**Primary Keys:** Ensure unique identification of records  
**Foreign Keys:** Maintain referential integrity between tables  
**Unique Constraints:** Prevent duplicate usernames, emails, and student IDs  
**Not Null:** Required fields cannot be empty  
**Cascade Delete:** Deleting session removes associated attendance records

## Indexing Strategy

**Indexed Columns:**
- `users.username`, `users.email` - Fast login queries
- `students.student_id` - Quick student lookup
- `sessions.instructor_id`, `sessions.status` - Session filtering
- `attendance.student_id`, `attendance.session_id`, `attendance.date` - Report generation

This database design supports efficient data management, maintains data integrity, and enables fast query performance for the Smart Attendance System.
