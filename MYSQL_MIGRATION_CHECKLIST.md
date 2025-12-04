# MySQL Migration Checklist

## 📋 Pre-Migration Checklist

- [ ] **Backup MongoDB data**
  ```cmd
  mongodump --db smart_attendance --out backup_mongodb
  ```

- [ ] **MySQL Server installed**
  - Download from: https://dev.mysql.com/downloads/mysql/
  - Version: 8.0 or higher recommended

- [ ] **MySQL Service running**
  ```cmd
  net start MySQL80
  ```

- [ ] **Know your MySQL root password**

- [ ] **Backend server stopped**

---

## 📋 Migration Steps Checklist

### ✅ Step 1: Create MySQL Database
- [ ] Open Command Prompt as Administrator
- [ ] Navigate to project directory
- [ ] Run database setup:
  ```cmd
  mysql -u root -p < setup_mysql_database.sql
  ```
- [ ] Verify tables created:
  ```sql
  USE smart_attendance;
  SHOW TABLES;
  ```
  Should show: users, students, sessions, attendance

### ✅ Step 2: Install MySQL Connector
- [ ] Navigate to backend directory:
  ```cmd
  cd backend
  ```
- [ ] Install connector:
  ```cmd
  pip install mysql-connector-python==9.1.0
  ```
- [ ] Verify installation:
  ```cmd
  pip show mysql-connector-python
  ```

### ✅ Step 3: Configure Environment
- [ ] Copy example file:
  ```cmd
  copy backend\.env.mysql.example backend\.env
  ```
- [ ] Edit `backend/.env` file
- [ ] Set MySQL credentials:
  ```env
  MYSQL_HOST=localhost
  MYSQL_PORT=3306
  MYSQL_DATABASE=smart_attendance
  MYSQL_USER=root
  MYSQL_PASSWORD=your_actual_password_here
  ```
- [ ] Save file

### ✅ Step 4: Run Data Migration
- [ ] **IMPORTANT**: Ensure MongoDB is still running!
- [ ] Run migration script:
  ```cmd
  migrate_to_mysql.bat
  ```
  OR manually:
  ```cmd
  cd backend
  python migrate_mongo_to_mysql.py
  ```
- [ ] Watch for success messages:
  - ✅ Users migration complete
  - ✅ Students migration complete
  - ✅ Sessions migration complete
  - ✅ Attendance migration complete

### ✅ Step 5: Verify Data Migration
- [ ] Login to MySQL:
  ```cmd
  mysql -u root -p
  ```
- [ ] Check data:
  ```sql
  USE smart_attendance;
  
  SELECT COUNT(*) as users FROM users;
  SELECT COUNT(*) as students FROM students;
  SELECT COUNT(*) as sessions FROM sessions;
  SELECT COUNT(*) as attendance FROM attendance;
  
  -- Sample data
  SELECT * FROM users LIMIT 5;
  SELECT * FROM students LIMIT 5;
  ```
- [ ] Verify counts match MongoDB

### ✅ Step 6: Test Backend
- [ ] Start backend:
  ```cmd
  cd backend
  python app.py
  ```
- [ ] Look for success message:
  ```
  ✅ Connected to MySQL: smart_attendance
  ```
- [ ] No errors in console
- [ ] Server running on http://localhost:5000

### ✅ Step 7: Test Application
- [ ] Open browser to http://localhost:5000/health
- [ ] Should see: `{"status": "healthy"}`
- [ ] Start frontend:
  ```cmd
  cd frontend
  npm run dev
  ```
- [ ] Test login with existing credentials
- [ ] Verify dashboard loads
- [ ] Check attendance records display
- [ ] Test session creation (if instructor)
- [ ] Test face recognition (if applicable)

---

## 📋 Post-Migration Checklist

### ✅ Verification
- [ ] All users can login
- [ ] Student data displays correctly
- [ ] Attendance records are visible
- [ ] Sessions work properly
- [ ] Face recognition works
- [ ] No console errors
- [ ] All features functional

### ✅ Cleanup
- [ ] Keep MongoDB running for 1-2 weeks (safety)
- [ ] Document any issues found
- [ ] Update team about migration
- [ ] Schedule MongoDB removal (after confirmation)

### ✅ Optimization
- [ ] Monitor query performance
- [ ] Check slow query log
- [ ] Add indexes if needed
- [ ] Configure MySQL settings

### ✅ Backup Strategy
- [ ] Set up automated MySQL backups:
  ```cmd
  mysqldump -u root -p smart_attendance > backup_%date%.sql
  ```
- [ ] Test backup restoration
- [ ] Document backup procedure
- [ ] Schedule regular backups

---

## 📋 Blueprint Update Checklist

**Note**: These files need to be updated to use MySQL queries instead of MongoDB:

- [ ] `backend/blueprints/auth.py`
  - Login
  - Register
  - Token validation

- [ ] `backend/blueprints/admin.py`
  - User management
  - System settings
  - Reports

- [ ] `backend/blueprints/students.py`
  - Student CRUD
  - Face registration
  - Student queries

- [ ] `backend/blueprints/attendance.py`
  - Record attendance
  - Get attendance
  - Session management

- [ ] `backend/blueprints/instructor.py`
  - Session creation
  - Attendance viewing
  - Reports

- [ ] `backend/blueprints/debug.py`
  - Debug endpoints
  - System info

**I can help you update these files one by one!**

---

## 🚨 Rollback Checklist (If Needed)

If something goes wrong:

- [ ] Stop backend server
- [ ] Restore MongoDB imports:
  ```python
  # In backend/app.py
  from db.mongo import init_db  # Change back
  ```
- [ ] Update `.env` with MongoDB settings
- [ ] Restart backend
- [ ] Verify MongoDB connection
- [ ] Test application

---

## 📊 Success Criteria

Migration is successful when:

- ✅ All data migrated (users, students, sessions, attendance)
- ✅ Backend connects to MySQL without errors
- ✅ Users can login
- ✅ All features work as before
- ✅ No data loss
- ✅ Performance is acceptable
- ✅ No console errors

---

## 📞 Support

If you encounter issues:

1. **Check Documentation**
   - MYSQL_MIGRATION_COMPLETE_GUIDE.md
   - MYSQL_MIGRATION_QUICK_START.md
   - MYSQL_MIGRATION_SUMMARY.md

2. **Common Issues**
   - MySQL not running: `net start MySQL80`
   - Access denied: Check password in `.env`
   - Migration fails: Ensure MongoDB is running
   - Connection errors: Verify MySQL credentials

3. **Get Help**
   - Review error messages
   - Check MySQL error log
   - Verify all prerequisites met
   - Ask with specific error details

---

## ✨ Current Status

**Date**: _____________

**Completed Steps**:
- [ ] Pre-migration backup
- [ ] MySQL installed
- [ ] Database created
- [ ] Connector installed
- [ ] Environment configured
- [ ] Data migrated
- [ ] Backend tested
- [ ] Application tested
- [ ] Verification complete

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

**Next Action**:
_____________________________________________

---

**Ready to start? Begin with Step 1!**
