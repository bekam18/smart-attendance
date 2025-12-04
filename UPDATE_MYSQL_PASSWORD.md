# ⚠️ IMPORTANT: Update MySQL Password

## 🔑 You Need to Add Your MySQL Password

The `.env` file has been updated, but you need to add your MySQL root password.

---

## 📋 Steps:

### 1. Open the file:
```
backend/.env
```

### 2. Find this line:
```env
MYSQL_PASSWORD=
```

### 3. Add your MySQL password:
```env
MYSQL_PASSWORD=your_actual_mysql_password_here
```

**IMPORTANT:** Use the same password you use to login to MySQL Workbench!

---

## 💡 How to Find Your MySQL Password

### If you remember it:
- Just type it after `MYSQL_PASSWORD=`

### If you forgot it:
1. Open MySQL Workbench
2. Try to connect - it will ask for password
3. Use that same password in `.env` file

### If you never set a password:
- Try leaving it empty: `MYSQL_PASSWORD=`
- Or try common defaults: `MYSQL_PASSWORD=root` or `MYSQL_PASSWORD=admin`

---

## ✅ Example `.env` file:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=smart_attendance
MYSQL_USER=root
MYSQL_PASSWORD=MySecurePassword123

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_EXPIRY_HOURS=24
```

---

## 🚀 After Adding Password:

Run the seed script again:
```cmd
cd backend
python seed_mysql_database.py
```

---

## 🆘 Still Getting "Access Denied"?

### Option 1: Reset MySQL Root Password

1. Open MySQL Workbench
2. Go to Server → Users and Privileges
3. Select 'root' user
4. Click "Change Password"
5. Set a new password
6. Use that password in `.env` file

### Option 2: Create New MySQL User

In MySQL Workbench, run:
```sql
CREATE USER 'smartattendance'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON smart_attendance.* TO 'smartattendance'@'localhost';
FLUSH PRIVILEGES;
```

Then update `.env`:
```env
MYSQL_USER=smartattendance
MYSQL_PASSWORD=password123
```

---

## 📞 Quick Test

After updating password, test the connection:
```cmd
cd backend
python -c "from db.mysql import get_db; db = get_db(); print('✅ Connected!')"
```

If you see `✅ Connected!`, you're good to go!

---

**Next Step:** Update `backend/.env` with your MySQL password, then run `python seed_mysql_database.py`
