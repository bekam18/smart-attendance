# Fix Login 401 Error - Step by Step Guide

## 🔍 Problem
You're getting a 401 Unauthorized error when trying to login, even with correct credentials.

## 🎯 Most Likely Cause
**The database hasn't been seeded with demo users yet.**

## ✅ Solution (Follow These Steps)

### Step 1: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
cd backend
venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install Dependencies (if not done)

```bash
pip install -r requirements.txt
```

### Step 3: Check Database Status

```bash
python check_db.py
```

This will tell you:
- How many users are in the database
- List all existing users
- Whether you need to seed the database

### Step 4: Seed the Database

If Step 3 shows 0 users, run:

```bash
python seed_db.py
```

This creates demo users:
- **Admin:** username: `admin`, password: `admin123`
- **Instructor:** username: `instructor`, password: `inst123`
- **Student:** username: `student`, password: `stud123`

### Step 5: Restart Backend Server

Stop the current server (Ctrl+C) and restart:

```bash
python app.py
```

### Step 6: Test Login

Now try logging in again from the frontend with:
- Username: `admin`
- Password: `admin123`

## 🔍 Debug Mode (See What's Happening)

I've added debug logging to the login route. When you try to login, you'll now see in the backend terminal:

```
🔍 Login attempt - Received data: {'username': 'admin', 'password': 'admin123'}
🔍 Looking for user: admin
✅ User found: admin
🔍 Verifying password...
✅ Password verified successfully for user: admin
```

Or if there's an issue:

```
🔍 Login attempt - Received data: {'username': 'admin', 'password': 'admin123'}
🔍 Looking for user: admin
❌ User not found: admin
💡 Hint: Have you run 'python seed_db.py' to create demo users?
```

## 🧪 Test Login via Command Line

You can also test the login endpoint directly:

```bash
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Expected Response (Success):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "...",
    "username": "admin",
    "email": "admin@smartattendance.com",
    "role": "admin",
    "name": "System Administrator"
  }
}
```

**Expected Response (Failure):**
```json
{
  "error": "Invalid credentials"
}
```

## 🔧 Other Possible Issues

### Issue 1: MongoDB Connection Problem

**Check your `.env` file:**
```bash
type backend\.env
```

Make sure `MONGODB_URI` is set correctly:
```env
MONGODB_URI=mongodb+srv://bekamayela18_db_user:2qBIVM2Qn3IZDAQy@cluster0.ifaywcg.mongodb.net/
```

**Test MongoDB connection:**
```bash
python -c "from pymongo import MongoClient; client = MongoClient('your-uri-here'); print('Connected:', client.server_info())"
```

### Issue 2: Wrong Password Format

The frontend might be sending the password in the wrong format. Check the frontend console (F12) for any errors.

### Issue 3: CORS Issues

If you see CORS errors in the browser console, make sure your backend `.env` has:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue 4: Password Hash Mismatch

If you manually created users without using `seed_db.py`, the passwords might not be hashed correctly.

**Solution:** Delete all users and re-seed:
```bash
python -c "from db.mongo import get_db; db = get_db(); db.users.delete_many({}); print('Users deleted')"
python seed_db.py
```

## 📝 Quick Checklist

- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database seeded (`python seed_db.py`)
- [ ] Backend server running (`python app.py`)
- [ ] MongoDB connection working (check terminal output)
- [ ] Using correct credentials (admin/admin123)
- [ ] Frontend pointing to correct API URL (check frontend/.env)

## 🎯 Expected Terminal Output (Success)

When login works, you should see:

**Backend Terminal:**
```
🔍 Login attempt - Received data: {'username': 'admin', 'password': 'admin123'}
🔍 Looking for user: admin
✅ User found: admin
🔍 Verifying password...
✅ Password verified successfully for user: admin
127.0.0.1 - - [24/Nov/2025 19:45:00] "POST /api/auth/login HTTP/1.1" 200 -
```

**Frontend (Browser Console):**
```
Login successful
Redirecting to /admin
```

## 🆘 Still Not Working?

If you've followed all steps and it's still not working:

1. **Check the debug output** in the backend terminal
2. **Check browser console** (F12) for errors
3. **Verify the request payload** in Network tab (F12 → Network → login request → Payload)
4. **Check MongoDB Atlas** - ensure your IP is whitelisted

### Get More Debug Info

Add this to your frontend login code to see what's being sent:

```typescript
console.log('Sending login request:', { username, password });
```

## 📞 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Username and password required" | Missing data in request | Check frontend is sending JSON correctly |
| "Invalid credentials" (user not found) | User doesn't exist in DB | Run `python seed_db.py` |
| "Invalid credentials" (password wrong) | Wrong password or hash mismatch | Use correct password or re-seed DB |
| "User not found" | Database connection issue | Check MongoDB URI |

## ✅ Success!

Once login works, you should:
1. See a success message in the frontend
2. Be redirected to the appropriate dashboard (admin/instructor/student)
3. See the JWT token stored in localStorage (F12 → Application → Local Storage)

---

**Need more help?** Check the backend terminal output with the new debug logging!
