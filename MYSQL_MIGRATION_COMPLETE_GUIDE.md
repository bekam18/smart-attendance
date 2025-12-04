# Complete MongoDB to MySQL Migration Guide

## 🎯 Overview

This guide will walk you through migrating your SmartAttendance system from MongoDB to MySQL step by step.

---

## ✅ Prerequisites

Before starting, ensure you have:
- MySQL Server installed
- Access to MySQL root account
- Current MongoDB data backed up
- Backend server stopped

---

## 📋 STEP 1: Install MySQL Server

### Windows:
1. Download MySQL Community Server from: https://dev.mysql.com/downloads/mysql/
2. Run the installer
3. Choose "Developer Default" setup type
4. Set a root password (remember this!)
5. Complete the installation

### Verify Installation:
```cmd
mysql --version
```

---

## 📋 STEP 2: Create MySQL Database

### Option A: Using MySQL Command Line

1. Open Command Prompt as Administrator
2. Login to MySQL:
```cmd
mysql -u root -p
```
3. Enter your root password
4. Run the setup script:
```sql
source C:/path/to/your/project/setup_mysql_database.sql
```

### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your local MySQL server
3. Open the file `setup_mysql_database.sql`
4. Click "Execute" (lightning bolt icon)
5. Verify all tables are created

### Option C: Manual Command Line

```cmd
mysql -u root -p < setup_mysql_database.sql
```

### Verify Database Created:
```sql
USE smart_attendance;
SHOW TABLES;
```

You should see:
- users
- students
- sessions
- attendance

---

## 📋 STEP 3: Install MySQL Python Connector

```cmd
cd backend
pip install mysql-connector-python==9.1.0
```

---

## 📋 STEP 4: Update Environment Configuration

1. Copy the example file:
```cmd
copy backend\.env.mysql.example backend\.env
```

2. Edit `backend/.env` with your MySQL credentials:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=smart_attendance
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_mysql_password

JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRY_HOURS=168
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
RECOGNITION_CONFIDENCE_THRESHOLD=0.60
```

---

## 📋 STEP 5: Migrate Data from MongoDB to MySQL

**IMPORTANT**: Make sure MongoDB is still running for this step!

```cmd
cd backend
python migrate_mongo_to_mysql.py
```

This will:
- ✅ Migrate all users
- ✅ Migrate all students
- ✅ Migrate all sessions
- ✅ Migrate all attendance records

Expected output:
```
================================================================================
MONGODB TO MYSQL MIGRATION
================================================================================

🚀 Starting Users migration...
✅ Migrated user: admin (admin)
✅ Migrated user: instructor1 (instructor)
...
✅ Users migration complete: X/X migrated

🚀 Starting Students migration...
✅ Migrated student: S001 - Student Name
...
✅ Students migration complete: X/X migrated

🚀 Starting Sessions migration...
✅ Migrated session: Session Name
...
✅ Sessions migration complete: X/X migrated

🚀 Starting Attendance migration...
✅ Migrated 100 attendance records...
...
✅ Attendance migration complete: X/X migrated

================================================================================
MIGRATION SUMMARY
================================================================================
Completed: 4/4 migrations

🎉 All migrations completed successfully!
```

---

## 📋 STEP 6: Verify Data Migration

Connect to MySQL and verify data:

```sql
USE smart_attendance;

-- Check users
SELECT COUNT(*) as user_count FROM users;
SELECT * FROM users LIMIT 5;

-- Check students
SELECT COUNT(*) as student_count FROM students;
SELECT * FROM students LIMIT 5;

-- Check sessions
SELECT COUNT(*) as session_count FROM sessions;
SELECT * FROM sessions LIMIT 5;

-- Check attendance
SELECT COUNT(*) as attendance_count FROM attendance;
SELECT * FROM attendance LIMIT 5;
```

---

## 📋 STEP 7: Test the Application

1. Start the backend:
```cmd
cd backend
python app.py
```

2. Look for successful connection message:
```
✅ Connected to MySQL: smart_attendance
```

3. Test login at: http://localhost:5000/api/auth/login

4. Test the frontend:
```cmd
cd frontend
npm run dev
```

5. Login and verify:
- ✅ Users can login
- ✅ Dashboard loads
- ✅ Attendance records display
- ✅ Sessions work
- ✅ Face recognition works

---

## 📋 STEP 8: Update All Blueprint Files

The migration has updated the database layer. Now we need to update all blueprint files to use MySQL syntax instead of MongoDB.

### Files that need updating:
- `backend/blueprints/auth.py`
- `backend/blueprints/admin.py`
- `backend/blueprints/students.py`
- `backend/blueprints/attendance.py`
- `backend/blueprints/instructor.py`
- `backend/blueprints/debug.py`

**I will help you update these files one by one in the next steps.**

---

## 🔧 Troubleshooting

### Error: "Access denied for user"
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON smart_attendance.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "Can't connect to MySQL server"
- Check if MySQL service is running:
```cmd
net start MySQL80
```

### Error: "Database does not exist"
- Re-run the setup script:
```cmd
mysql -u root -p < setup_mysql_database.sql
```

### Error: "Table already exists"
- Drop and recreate:
```sql
DROP DATABASE smart_attendance;
CREATE DATABASE smart_attendance;
```
Then re-run setup script.

---

## 📊 Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'instructor', 'student') NOT NULL,
    department VARCHAR(100),
    course_name VARCHAR(100),
    class_year VARCHAR(20),
    session_types JSON,
    sections JSON,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Students Table
```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(100),
    year VARCHAR(20),
    section VARCHAR(20),
    face_registered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT NOT NULL,
    instructor_name VARCHAR(100),
    section_id VARCHAR(50),
    session_type ENUM('lab', 'theory'),
    course_name VARCHAR(100),
    class_year VARCHAR(20),
    name VARCHAR(200),
    course VARCHAR(100),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('active', 'ended') DEFAULT 'active',
    attendance_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    session_id INT NOT NULL,
    instructor_id INT NOT NULL,
    section_id VARCHAR(50),
    session_type ENUM('lab', 'theory'),
    course_name VARCHAR(100),
    class_year VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE NOT NULL,
    confidence DECIMAL(5,4),
    status ENUM('present', 'absent') DEFAULT 'present',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, session_id, date)
);
```

---

## 🎉 Benefits of MySQL

### Performance
- ✅ Faster queries with proper indexing
- ✅ Better JOIN performance
- ✅ Optimized for relational data

### Management
- ✅ Familiar SQL syntax
- ✅ Better tooling (MySQL Workbench, phpMyAdmin)
- ✅ Easier backup and restore

### Compatibility
- ✅ Wider hosting support
- ✅ Better integration with BI tools
- ✅ Standard ACID compliance

### Features
- ✅ Foreign key constraints
- ✅ Transactions
- ✅ Stored procedures
- ✅ Views and triggers

---

## 🔄 Rollback Plan

If you need to rollback to MongoDB:

1. Keep MongoDB data until migration is confirmed working
2. Restore MongoDB imports in code:
   - Change `from db.mysql import init_db` back to `from db.mongo import init_db`
3. Update `.env` to use MongoDB configuration
4. Restart application

---

## 📝 Next Steps

After completing this migration:

1. ✅ Test all features thoroughly
2. ✅ Update all blueprint files (I'll help with this)
3. ✅ Set up regular MySQL backups
4. ✅ Monitor performance
5. ✅ Update documentation

---

## 🆘 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify MySQL service is running
3. Check `.env` configuration
4. Review migration script output for errors
5. Ask for help with specific error messages

---

**Status**: Ready for migration
**Estimated Time**: 30-60 minutes
**Difficulty**: Medium
