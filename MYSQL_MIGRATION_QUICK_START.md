# MySQL Migration - Quick Start

## 🚀 Fast Track (5 Steps)

### 1️⃣ Install MySQL
Download and install MySQL Community Server:
- Windows: https://dev.mysql.com/downloads/mysql/
- Set root password during installation

### 2️⃣ Create Database
```cmd
mysql -u root -p < setup_mysql_database.sql
```

### 3️⃣ Run Migration Script
```cmd
migrate_to_mysql.bat
```

### 4️⃣ Configure Environment
Edit `backend/.env`:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=smart_attendance
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
```

### 5️⃣ Test Application
```cmd
cd backend
python app.py
```

---

## ✅ Verification Checklist

- [ ] MySQL installed and running
- [ ] Database `smart_attendance` created
- [ ] Tables created (users, students, sessions, attendance)
- [ ] MySQL connector installed (`pip install mysql-connector-python`)
- [ ] `.env` file configured with MySQL credentials
- [ ] Data migrated from MongoDB
- [ ] Backend starts without errors
- [ ] Can login to application
- [ ] Attendance records visible

---

## 🔧 Quick Commands

### Check MySQL Status
```cmd
net start MySQL80
```

### Login to MySQL
```cmd
mysql -u root -p
```

### Verify Database
```sql
USE smart_attendance;
SHOW TABLES;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM students;
SELECT COUNT(*) FROM attendance;
```

### Start Backend
```cmd
cd backend
python app.py
```

---

## ⚠️ Common Issues

**Can't connect to MySQL**
```cmd
net start MySQL80
```

**Access denied**
```sql
GRANT ALL PRIVILEGES ON smart_attendance.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

**Migration fails**
- Make sure MongoDB is still running
- Check MongoDB has data to migrate
- Verify MySQL database exists

---

## 📚 Full Documentation

For detailed step-by-step instructions, see:
**MYSQL_MIGRATION_COMPLETE_GUIDE.md**

---

## 🎯 What Changed

### Files Created:
- ✅ `setup_mysql_database.sql` - Database schema
- ✅ `backend/db/mysql.py` - MySQL connection
- ✅ `backend/migrate_mongo_to_mysql.py` - Data migration
- ✅ `migrate_to_mysql.bat` - Automated migration
- ✅ `backend/.env.mysql.example` - Config template

### Files Modified:
- ✅ `backend/config.py` - Added MySQL config
- ✅ `backend/app.py` - Changed to MySQL import
- ✅ `backend/requirements.txt` - Added MySQL connector

### Next Steps:
- Update blueprint files to use MySQL queries
- Test all features
- Remove MongoDB dependency

---

**Ready to migrate? Run:** `migrate_to_mysql.bat`
