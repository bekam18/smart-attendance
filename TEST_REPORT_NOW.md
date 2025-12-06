# Test Report Generation - Quick Guide

## ✅ WORKING PARAMETERS

### For Instructor "bacha" (username: bacha)
Login with:
- Username: `bacha`
- Password: (your password)

Then generate report with:
- **Course**: `Mobile Development` ⚠️ NOT "Web"
- **Section**: `A`
- **Start Date**: `2025-12-01` ⚠️ NOT 2024
- **End Date**: `2025-12-31`

### Expected Results
```
Total Sessions: 1
Total Students: 12

Student Breakdown:
- STU001 (Nabila): 0 present, 1 absent (not in attendance record)
- STU002 (Nardos): 0 present, 1 absent
- STU003 (Amanu): 0 present, 1 absent
- STU004 (Gadisa): 0 present, 1 absent
- STU005 (Yonas): 0 present, 1 absent
- STU006: 0 present, 1 absent
- STU008: 0 present, 1 absent
- STU009: 0 present, 1 absent
- STU010: 0 present, 1 absent
- STU011: 0 present, 1 absent
- STU012: 0 present, 1 absent
- STU013: 1 present, 0 absent ✅
```

---

## ❌ WRONG PARAMETERS (Will Show 0 Sessions)

### Don't Use These:
- ❌ Course: "Web" (no data exists for Web yet)
- ❌ Date: 2024-12-01 to 2024-12-31 (data is in 2025)

---

## For Instructor "bekam" (username: beki)
Login with:
- Username: `beki`
- Password: (your password)

Then generate report with:
- **Course**: `OS` ⚠️ NOT "Java"
- **Section**: `A`
- **Start Date**: `2025-12-01`
- **End Date**: `2025-12-31`

### Expected Results
```
Total Sessions: 1
Total Students: 12

Student Breakdown:
- 10 students: 0 present, 1 absent
- STU013: 1 present, 0 absent ✅
- STU001: not in attendance (0 present, 1 absent)
```

---

## Why Some Courses Show No Data

### Current Data Status:
| Instructor | Courses in Profile | Courses with Attendance Data |
|------------|-------------------|------------------------------|
| bacha      | Web, Mobile Dev   | ✅ Mobile Dev only           |
| bekam      | Java, OS          | ✅ OS only                   |

### To Get Data for "Web" or "Java":
1. Create a session for that course
2. Record attendance for that session
3. Then reports will work

---

## Quick Test Commands

```bash
# Test with correct parameters
python test_report_with_correct_course.py

# Check what data exists
python check_actual_data.py

# Check instructor courses
python check_instructor_courses.py

# Diagnose any issues
python diagnose_report_query.py
```

---

## Summary

✅ **Report generation is working correctly**
✅ **No bugs in the code**
✅ **Issue was selecting wrong course/date**

**Solution**: Use "Mobile Development" (not "Web") and dates in 2025 (not 2024)
