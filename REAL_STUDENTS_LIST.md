# 🎓 Real Student List - Login Credentials

## 📊 Student Database

**Total Students**: 19  
**Sections**: A, B, C

---

## 👥 Section A (6 students)

| Student ID | Name | Username | Password | Section |
|------------|------|----------|----------|---------|
| STU001 | Nabila | STU001 | Nabila123 | A |
| STU002 | Nardos | STU002 | Nardos123 | A |
| STU003 | Amanu | STU003 | Amanu123 | A |
| STU004 | Gadisa Tegene | STU004 | Gadisa123 | A |
| STU005 | Yonas | STU005 | Yonas123 | A |
| STU006 | Merihun | STU006 | Merihun123 | A |

---

## 👥 Section B (7 students)

| Student ID | Name | Username | Password | Section |
|------------|------|----------|----------|---------|
| STU008 | Nutoli | STU008 | Nutoli123 | B |
| STU009 | Tedy | STU009 | Tedy123 | B |
| STU010 | Ajme | STU010 | Ajme123 | B |
| STU011 | Bedo | STU011 | Bedo123 | B |
| STU012 | Milki | STU012 | Milki123 | B |
| STU013 | Bekam Ayele | STU013 | Bekam123 | B |
| STU014 | Yabsira | STU014 | Yabsira123 | B |

---

## 👥 Section C (6 students)

| Student ID | Name | Username | Password | Section |
|------------|------|----------|----------|---------|
| STU015 | Firansbekan | STU015 | Firansbekan123 | C |
| STU016 | Bacha Eshetu | STU016 | Bacha123 | C |
| STU017 | Yohannis Tekelgin | STU017 | Yohannis123 | C |
| STU018 | Bari | STU018 | Bari123 | C |
| STU019 | Lami | STU019 | Lami123 | C |
| STU021 | Yien | STU021 | Yien123 | C |

---

## 🔐 Login Pattern

**Username**: Student ID (e.g., STU001)  
**Password**: {FirstName}123 (e.g., Nabila123)

### Examples:
- **Nabila** → Password: `Nabila123`
- **Gadisa Tegene** → Password: `Gadisa123` (first name only)
- **Bekam Ayele** → Password: `Bekam123` (first name only)

---

## 🚀 Installation

### Run the update script:
```bash
update_students.bat
```

This will:
- ✅ Remove all test students
- ✅ Add 19 real students
- ✅ Preserve admin/instructor accounts
- ✅ Keep attendance/session data unchanged

---

## 📝 What Gets Updated

### Updated Collections:
- ✅ `users` - Student user accounts
- ✅ `students` - Student profiles

### Preserved Collections:
- ✅ `users` (admin/instructor) - Unchanged
- ✅ `sessions` - Unchanged
- ✅ `attendance` - Unchanged
- ✅ `user_settings` - Unchanged

---

## 🎯 Next Steps for Students

1. **Login** with student_id and password
2. **Register Face** (required for attendance)
3. **Attend Sessions** (face recognition)

---

## 👨‍🏫 For Instructors

Students are now organized by sections:
- **Section A**: 6 students
- **Section B**: 7 students  
- **Section C**: 6 students

You can create sessions for specific sections and take attendance.

---

## 🔍 Verification

After running the update script, verify:

```bash
# Check student count
cd backend
python -c "from pymongo import MongoClient; from config import config; client = MongoClient(config.MONGODB_URI); db = client[config.MONGODB_DB_NAME]; print(f'Students: {db.students.count_documents({})}'); print(f'Section A: {db.students.count_documents({\"section\": \"A\"})}'); print(f'Section B: {db.students.count_documents({\"section\": \"B\"})}'); print(f'Section C: {db.students.count_documents({\"section\": \"C\"})}')"
```

Expected output:
```
Students: 19
Section A: 6
Section B: 7
Section C: 6
```

---

## 📧 Student Email Format

Auto-generated emails: `{student_id}@student.edu`

Examples:
- STU001@student.edu
- STU002@student.edu
- etc.

---

## ✅ Status

- ✅ Script created: `backend/update_real_students.py`
- ✅ Batch file created: `update_students.bat`
- ✅ Documentation created: `REAL_STUDENTS_LIST.md`
- ✅ Ready to run

**Run `update_students.bat` to update the database!** 🚀
