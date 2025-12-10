# 5.3.3 Persistence Diagram

The Persistence Diagram illustrates how data is stored and maintained in the Smart Attendance System. It shows the database structure, data flow, and persistence mechanisms that ensure data integrity and availability across system sessions.

## Data Persistence Architecture

The system uses MySQL for persistent storage with the following characteristics:

**Transactional Support:** ACID properties ensure data consistency  
**Relational Integrity:** Foreign key constraints maintain relationships  
**Indexed Access:** Optimized queries for fast data retrieval  
**Backup Support:** Regular backups prevent data loss

## Persistent Entities

### 1. User Authentication Data
**Table:** Users  
**Persistence:** Login credentials, roles, and profile information  
**Lifetime:** Permanent (until account deletion)  
**Access:** Authenticated via JWT tokens with 24-hour expiration

### 2. Student Profile Data
**Table:** Students  
**Persistence:** Student ID, name, email, section, year, department  
**Lifetime:** Academic enrollment period + 2 years  
**Access:** Linked to user account via foreign key

### 3. Session Data
**Table:** Sessions  
**Persistence:** Session details, status, timestamps, course information  
**Lifetime:** Academic year + archival period  
**Access:** Instructor-specific with status-based filtering

### 4. Attendance Records
**Table:** Attendance  
**Persistence:** Student attendance with timestamp, confidence, and status  
**Lifetime:** Permanent (academic records)  
**Access:** Role-based (instructors see own courses, students see own records)

## Data Flow and Persistence

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Authentication│  │   Session    │  │  Attendance  │     │
│  │    Module     │  │  Management  │  │   Logger     │     │
│  └───────┬────────┘  └───────┬──────┘  └───────┬──────┘     │
│          │                   │                  │            │
└──────────┼───────────────────┼──────────────────┼────────────┘
           │                   │                  │
           ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER (MySQL)                 │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Users     │  │   Students   │  │   Sessions   │     │
│  │   Table      │  │    Table     │  │    Table     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                     ┌──────▼───────┐                        │
│                     │  Attendance  │                        │
│                     │    Table     │                        │
│                     └──────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER (Disk)                      │
│  • MySQL Data Files (.ibd)                                  │
│  • Transaction Logs (ib_logfile)                            │
│  • Binary Logs (for replication)                            │
└─────────────────────────────────────────────────────────────┘
```

## Persistence Mechanisms

### Data Creation
- **User Registration:** Admin creates user accounts, data persisted immediately
- **Session Creation:** Instructor starts session, record created with active status
- **Attendance Recording:** Face recognition triggers attendance record creation
- **Transaction:** All writes wrapped in database transactions for consistency

### Data Retrieval
- **Login:** Query users table with username, verify hashed password
- **Session List:** Query sessions table filtered by instructor ID and status
- **Attendance History:** Query attendance table with student/date filters
- **Reports:** Aggregate queries with date range and course filters

### Data Updates
- **Password Change:** Update hashed password in users table
- **Session Status:** Update status field (active → stopped_daily → ended_semester)
- **Attendance Timestamp:** Update existing record on duplicate recognition
- **Profile Updates:** Modify student or instructor information

### Data Deletion
- **Cascade Delete:** Removing session deletes associated attendance records
- **Soft Delete:** User accounts can be disabled without data loss
- **Archival:** Old records retained for compliance and historical analysis

## Data Integrity Measures

**Primary Keys:** Unique identification for all records  
**Foreign Keys:** Enforce referential integrity between tables  
**Constraints:** NOT NULL, UNIQUE, CHECK constraints validate data  
**Transactions:** ACID properties ensure consistency  
**Indexes:** Speed up queries without compromising data integrity

## Backup and Recovery

**Automated Backups:** Daily database dumps to prevent data loss  
**Transaction Logs:** Enable point-in-time recovery  
**Replication:** Master-slave setup for high availability (optional)  
**Export Functions:** CSV/Excel exports provide additional data backup

This persistence architecture ensures reliable, consistent, and secure data storage throughout the system's lifecycle.
