# ⚠️ Tables Not Created - Quick Fix

## Problem
The error `Table 'smart_attendance.users' doesn't exist` means the tables weren't created in MySQL.

---

## ✅ Solution: Run SQL Script in MySQL Workbench

### Step 1: Open MySQL Workbench
- Launch MySQL Workbench 8.0
- Connect to your local MySQL instance

### Step 2: Open the SQL Script
1. Click **File → Open SQL Script**
2. Navigate to your project folder
3. Select **`setup_mysql_database.sql`**
4. Click **Open**

### Step 3: Execute the Script
1. Click the **⚡ Execute** button (lightning bolt icon)
2. Or press **Ctrl+Shift+Enter**
3. Wait for completion

### Step 4: Verify Tables Created
1. In the left sidebar, click the **refresh button** (🔄)
2. Expand **smart_attendance** → **Tables**
3. You should see:
   - ✅ users
   - ✅ students
   - ✅ sessions
   - ✅ attendance

---

## Alternative: Run from Command Line

If you prefer command line:

```cmd
mysql -u root -p smart_attendance < setup_mysql_database.sql
```

Enter your MySQL password when prompted.

---

## After Tables Are Created

Run the seed script again:

```cmd
cd backend
python seed_mysql_database.py
```

Type `yes` when prompted.

You should see:
```
✅ Admin user created
✅ Instructor user created
✅ Created student: S001 - Alice Johnson
✅ Created student: S002 - Bob Smith
✅ Created student: S003 - Charlie Brown
```

---

## Quick Verification in MySQL Workbench

After running the SQL script, verify with this query:

```sql
USE smart_attendance;
SHOW TABLES;
```

You should see 4 tables listed.

---

**Next Step:** Open MySQL Workbench and run `setup_mysql_database.sql`
