# MySQL Setup - Choose Your Option

## 🎯 You Have Two Options

---

## ✅ **Option 1: Fresh Start (No MongoDB Data)**

If you don't have MongoDB running or don't need to migrate old data, use this option to create fresh data in MySQL.

### Steps:

1. **Seed the database with initial data:**
   ```cmd
   cd backend
   python seed_mysql_database.py
   ```

2. **This will create:**
   - ✅ Admin user (username: `admin`, password: `admin123`)
   - ✅ Instructor user (username: `instructor1`, password: `instructor123`)
   - ✅ 3 Sample students (username: `s001`, `s002`, `s003`, password: `student123`)

3. **Start the backend:**
   ```cmd
   python app.py
   ```

4. **Test login:**
   - Open browser: http://localhost:5173
   - Login with admin credentials

---

## ✅ **Option 2: Migrate from MongoDB**

If you have MongoDB running with existing data, use this option.

### Prerequisites:
- MongoDB service must be running
- MongoDB must have data in `smart_attendance` database

### Steps:

1. **Start MongoDB service:**
   ```cmd
   net start MongoDB
   ```
   
   Or if using MongoDB Community:
   ```cmd
   "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" --dbpath="C:\data\db"
   ```

2. **Verify MongoDB is running:**
   ```cmd
   check_mongodb_status.bat
   ```

3. **Run migration:**
   ```cmd
   cd backend
   python migrate_mongo_to_mysql.py
   ```

4. **Start the backend:**
   ```cmd
   python app.py
   ```

---

## 🤔 **Which Option Should I Choose?**

### Choose **Option 1** (Fresh Start) if:
- ✅ You don't have MongoDB installed
- ✅ MongoDB is not running
- ✅ You don't have existing data to migrate
- ✅ You want to start fresh with MySQL
- ✅ You're setting up for the first time

### Choose **Option 2** (Migrate) if:
- ✅ You have MongoDB running
- ✅ You have existing users, students, and attendance data
- ✅ You want to preserve all your old data
- ✅ You're migrating an existing system

---

## 📋 **Quick Decision Guide**

Run this command to check if MongoDB is installed:
```cmd
check_mongodb_status.bat
```

**If you see:**
- "Service does not exist" → Use **Option 1** (Fresh Start)
- "Service is running" → Use **Option 2** (Migrate)
- "Service is stopped" → Start MongoDB, then use **Option 2**

---

## 🚀 **Recommended: Option 1 (Fresh Start)**

Since MongoDB is not currently running, I recommend **Option 1** to get started quickly:

```cmd
cd backend
python seed_mysql_database.py
```

Then test:
```cmd
python app.py
```

You can always add more users and students later through the admin interface!

---

## ✅ **After Setup (Both Options)**

1. **Verify database has data:**
   - Open MySQL Workbench
   - Connect to `smart_attendance`
   - Check tables have data:
     ```sql
     SELECT COUNT(*) FROM users;
     SELECT COUNT(*) FROM students;
     ```

2. **Start backend:**
   ```cmd
   cd backend
   python app.py
   ```
   
   Look for: `✅ Connected to MySQL: smart_attendance`

3. **Start frontend:**
   ```cmd
   cd frontend
   npm run dev
   ```

4. **Test login:**
   - Open: http://localhost:5173
   - Login with credentials from your chosen option

---

## 🆘 **Troubleshooting**

### Error: "Can't connect to MySQL"
**Solution:**
```cmd
net start MySQL80
```

### Error: "Access denied"
**Solution:** Check `backend/.env` has correct MySQL password

### Error: "No module named 'bcrypt'"
**Solution:**
```cmd
pip install bcrypt
```

### MongoDB won't start
**Solution:** Use Option 1 (Fresh Start) instead

---

## 📞 **Need Help?**

- **Option 1 issues:** Check MySQL connection in `.env` file
- **Option 2 issues:** Ensure MongoDB is running first
- **Both options:** Verify MySQL Workbench shows `smart_attendance` database

---

**Ready to proceed? Choose your option and follow the steps!**
