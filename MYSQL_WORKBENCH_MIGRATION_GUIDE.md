# MySQL Migration Using MySQL Workbench 8.0

## 🎯 Quick Guide for MySQL Workbench Users

Since you have MySQL Workbench 8.0, this is the easiest way to migrate!

---

## 📋 STEP 1: Open MySQL Workbench and Connect

1. **Open MySQL Workbench 8.0**
2. **Click on your Local MySQL connection** (usually "Local instance MySQL80")
3. **Enter your root password** when prompted
4. You should see the SQL Editor

---

## 📋 STEP 2: Create Database Using Workbench

### Option A: Using the SQL Script (Recommended)

1. In MySQL Workbench, click **File → Open SQL Script**
2. Navigate to your project folder
3. Select **`setup_mysql_database.sql`**
4. Click **Open**
5. Click the **⚡ Execute** button (lightning bolt icon) or press **Ctrl+Shift+Enter**
6. Wait for execution to complete

You should see:
```
✅ Database 'smart_attendance' created
✅ Table 'users' created
✅ Table 'students' created
✅ Table 'sessions' created
✅ Table 'attendance' created
```

### Option B: Manual Creation (Alternative)

If you prefer to create manually:

1. In the left sidebar, right-click on **Schemas**
2. Select **Create Schema**
3. Name it: `smart_attendance`
4. Click **Apply**
5. Then run the table creation queries from the script

---

## 📋 STEP 3: Verify Database Created

1. In the left sidebar under **Schemas**, you should see **smart_attendance**
2. Click the ▶ arrow next to it to expand
3. Click the ▶ arrow next to **Tables**
4. You should see 4 tables:
   - ✅ users
   - ✅ students
   - ✅ sessions
   - ✅ attendance

5. Right-click on **users** table → **Select Rows - Limit 1000**
6. It should be empty (no data yet)

---

## 📋 STEP 4: Install MySQL Python Connector

1. Open **Command Prompt** (not MySQL Workbench)
2. Navigate to your project:
   ```cmd
   cd path\to\your\project\backend
   ```
3. Install the connector:
   ```cmd
   pip install mysql-connector-python==9.1.0
   ```
4. Wait for installation to complete

---

## 📋 STEP 5: Configure Environment

1. Open your project in your code editor
2. Navigate to `backend` folder
3. Create a new file called `.env` (if it doesn't exist)
4. Copy the contents from `backend/.env.mysql.example`
5. Edit the MySQL password:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=smart_attendance
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_ACTUAL_MYSQL_PASSWORD_HERE

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRY_HOURS=168

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Face Recognition
RECOGNITION_CONFIDENCE_THRESHOLD=0.60
```

**IMPORTANT**: Replace `YOUR_ACTUAL_MYSQL_PASSWORD_HERE` with your actual MySQL root password!

---

## 📋 STEP 6: Run Data Migration

**IMPORTANT**: Make sure MongoDB is still running for this step!

1. Open **Command Prompt**
2. Navigate to backend:
   ```cmd
   cd path\to\your\project\backend
   ```
3. Run the migration script:
   ```cmd
   python migrate_mongo_to_mysql.py
   ```

You should see output like:
```
================================================================================
MONGODB TO MYSQL MIGRATION
================================================================================

📋 Migrating users...
✅ Migrated user: admin (admin)
✅ Migrated user: instructor1 (instructor)
✅ Users migration complete: X/X migrated

📋 Migrating students...
✅ Migrated student: S001 - Student Name
✅ Students migration complete: X/X migrated

📋 Migrating sessions...
✅ Migrated session: Session Name
✅ Sessions migration complete: X/X migrated

📋 Migrating attendance...
✅ Migrated 100 attendance records...
✅ Attendance migration complete: X/X migrated

================================================================================
MIGRATION SUMMARY
================================================================================
Completed: 4/4 migrations

🎉 All migrations completed successfully!
```

---

## 📋 STEP 7: Verify Data in MySQL Workbench

1. Go back to **MySQL Workbench**
2. Click the **refresh** button (🔄) in the Schemas panel
3. Expand **smart_attendance → Tables**
4. Right-click on **users** → **Select Rows - Limit 1000**
5. You should see your migrated users!

Repeat for other tables:
- **students** - Should show all students
- **sessions** - Should show all sessions
- **attendance** - Should show all attendance records

### Quick Verification Query

Run this in MySQL Workbench:
```sql
USE smart_attendance;

-- Count records in each table
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'attendance', COUNT(*) FROM attendance;
```

---

## 📋 STEP 8: Test Backend Connection

1. Open **Command Prompt**
2. Navigate to backend:
   ```cmd
   cd path\to\your\project\backend
   ```
3. Start the backend:
   ```cmd
   python app.py
   ```

Look for this message:
```
✅ Connected to MySQL: smart_attendance
🚀 SmartAttendance API running on http://0.0.0.0:5000
```

If you see this, **SUCCESS!** ✅

---

## 📋 STEP 9: Test the Application

1. Keep the backend running
2. Open a new Command Prompt
3. Navigate to frontend:
   ```cmd
   cd path\to\your\project\frontend
   ```
4. Start the frontend:
   ```cmd
   npm run dev
   ```
5. Open browser to: http://localhost:5173
6. Try to login with your credentials
7. Verify:
   - ✅ Login works
   - ✅ Dashboard loads
   - ✅ Attendance records display
   - ✅ All features work

---

## 🎉 Success Checklist

- [ ] MySQL Workbench connected
- [ ] Database `smart_attendance` created
- [ ] 4 tables created (users, students, sessions, attendance)
- [ ] MySQL connector installed
- [ ] `.env` file configured with password
- [ ] Data migration completed successfully
- [ ] Data visible in MySQL Workbench
- [ ] Backend starts without errors
- [ ] Can login to application
- [ ] All features working

---

## 🔧 Troubleshooting in MySQL Workbench

### Issue: Can't connect to MySQL
**Solution**: 
1. Check if MySQL service is running
2. In Windows: Services → MySQL80 → Start
3. Or run: `net start MySQL80`

### Issue: Access denied
**Solution**:
1. Verify password in MySQL Workbench connection
2. Update password in `backend/.env` to match

### Issue: Database not showing
**Solution**:
1. Click refresh button (🔄) in Schemas panel
2. Or run: `SHOW DATABASES;`

### Issue: Tables empty after migration
**Solution**:
1. Check migration script output for errors
2. Verify MongoDB is running
3. Re-run migration: `python migrate_mongo_to_mysql.py`

### Issue: Can't see data in tables
**Solution**:
1. Right-click table → Select Rows
2. Or run: `SELECT * FROM users LIMIT 10;`

---

## 💡 MySQL Workbench Tips

### View Table Structure
1. Right-click table → **Table Inspector**
2. See columns, indexes, foreign keys

### Run Queries
1. Click in SQL Editor area
2. Type your query
3. Press **Ctrl+Enter** to execute
4. Results appear below

### Export Data
1. Right-click table → **Table Data Export Wizard**
2. Choose format (CSV, JSON, SQL)
3. Save backup

### Import Data
1. Right-click table → **Table Data Import Wizard**
2. Select file
3. Map columns
4. Import

### Monitor Performance
1. **Performance → Dashboard**
2. See active connections, queries
3. Monitor server health

---

## 📊 Useful Queries for MySQL Workbench

### Check all data counts
```sql
USE smart_attendance;

SELECT 
    'users' as table_name, 
    COUNT(*) as total_records 
FROM users
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'attendance', COUNT(*) FROM attendance;
```

### View recent attendance
```sql
SELECT 
    a.student_id,
    s.name as student_name,
    a.timestamp,
    a.confidence,
    a.status
FROM attendance a
LEFT JOIN students s ON a.student_id = s.student_id
ORDER BY a.timestamp DESC
LIMIT 20;
```

### View active sessions
```sql
SELECT 
    id,
    instructor_name,
    course_name,
    session_type,
    start_time,
    status,
    attendance_count
FROM sessions
WHERE status = 'active'
ORDER BY start_time DESC;
```

### View users by role
```sql
SELECT 
    role,
    COUNT(*) as count
FROM users
GROUP BY role;
```

---

## 🎯 Next Steps

After successful migration:

1. ✅ **Test thoroughly** - Try all features
2. ✅ **Update blueprint files** - I can help with this
3. ✅ **Set up backups** - Use MySQL Workbench export
4. ✅ **Monitor performance** - Use Performance Dashboard
5. ✅ **Document changes** - Update team

---

## 📞 Need Help?

If you encounter any issues:

1. Check the error message in Command Prompt
2. Check MySQL Workbench for connection issues
3. Verify `.env` file has correct password
4. Ensure MongoDB is running during migration
5. Check the detailed guides:
   - MYSQL_MIGRATION_COMPLETE_GUIDE.md
   - MYSQL_MIGRATION_QUICK_START.md

---

**Ready to start? Open MySQL Workbench and begin with Step 1!** 🚀
