# Multi-Course Instructor - Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Run migration (one-time)
migrate_instructor_courses.bat

# 2. Start system
cd backend && python app.py
cd frontend && npm run dev

# 3. Login as admin and use!
```

## 📝 How to Add Instructor with Multiple Courses

### Step-by-Step

1. Click **"Add Instructor"** button
2. Fill in:
   - Username
   - Password
   - Email
   - Full Name
   - Department
   - Class Year
3. **Add Courses:**
   - Type course name
   - Press **Enter** OR click **"Add Course"**
   - Repeat for each course
4. **Remove courses:** Click **×** on any course tag
5. Select **Session Types** (Lab/Theory)
6. Click **"Add Instructor"**

### Example

```
Username: dr.smith
Email: smith@university.edu
Name: Dr. John Smith
Year: 3rd Year

Courses:
[Data Structures ×]
[Algorithms ×]
[Database Systems ×]

Type: [Enter course name...] [Add Course]
3 course(s) added

Sessions: ☑ Lab  ☑ Theory
```

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Multiple Courses** | Add unlimited courses per instructor |
| **Quick Add** | Press Enter to add course |
| **Easy Remove** | Click × to remove course |
| **Validation** | At least 1 course required |
| **Visual Tags** | Courses shown as colored badges |
| **Backward Compatible** | Old instructors still work |

## 📊 Table Display

Instructors now show multiple course badges:

```
┌──────────────┬────────────────────────────────┐
│ Name         │ Courses                        │
├──────────────┼────────────────────────────────┤
│ Dr. Smith    │ [Data Structures]              │
│              │ [Algorithms]                   │
│              │ [Database Systems]             │
├──────────────┼────────────────────────────────┤
│ Prof. Jones  │ [Machine Learning]             │
│              │ [AI Fundamentals]              │
└──────────────┴────────────────────────────────┘
```

## 🔧 API Format

### Add Instructor Request

```json
POST /api/admin/add-instructor
{
  "username": "dr.smith",
  "password": "password123",
  "email": "smith@university.edu",
  "name": "Dr. John Smith",
  "department": "Computer Science",
  "courses": [
    "Data Structures",
    "Algorithms",
    "Database Systems"
  ],
  "class_year": "3rd Year",
  "lab_session": true,
  "theory_session": true
}
```

### Get Instructors Response

```json
[
  {
    "id": "...",
    "name": "Dr. John Smith",
    "courses": [
      "Data Structures",
      "Algorithms",
      "Database Systems"
    ],
    "class_year": "3rd Year",
    "session_types": ["lab", "theory"],
    "enabled": true
  }
]
```

## ⚠️ Validation Rules

| Rule | Error Message |
|------|---------------|
| No courses added | "Please add at least one course" |
| No session type | "Please select at least one session type" |
| Duplicate course | Prevented automatically |
| Empty course name | Ignored automatically |

## 🔄 Migration

### One-Time Setup

```bash
migrate_instructor_courses.bat
```

This converts existing instructors from:
```json
{"course_name": "Data Structures"}
```

To:
```json
{"courses": ["Data Structures"]}
```

## 💡 Tips & Tricks

| Tip | Benefit |
|-----|---------|
| Press **Enter** after typing | Faster than clicking button |
| Click **×** to remove | Quick course removal |
| Add courses first | Then fill other fields |
| Use descriptive names | "Data Structures" not "DS" |

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "At least one course required" | Add at least 1 course before submitting |
| Courses not showing | Run migration script |
| Old instructors broken | System auto-converts, no action needed |
| Can't remove course | Click the × button on the course tag |

## 📁 Files Changed

### Frontend
- `frontend/src/pages/AdminDashboard.tsx`

### Backend
- `backend/blueprints/admin.py`

### New Files
- `backend/migrate_instructor_courses.py`
- `migrate_instructor_courses.bat`

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `INSTRUCTOR_MULTI_COURSE_COMPLETE.md` | Full technical docs |
| `MULTI_COURSE_QUICK_START.md` | Quick start guide |
| `IMPLEMENTATION_SUMMARY_MULTI_COURSE.md` | Implementation details |
| `MULTI_COURSE_REFERENCE_CARD.md` | This card |

## ✅ Checklist

Before using:
- [ ] Run migration script
- [ ] Start backend
- [ ] Start frontend
- [ ] Login as admin

When adding instructor:
- [ ] Fill basic info
- [ ] Add at least 1 course
- [ ] Select session type
- [ ] Submit

## 🎉 Benefits

✅ Realistic teaching assignments
✅ Flexible course management
✅ Easy to use interface
✅ Works with existing data
✅ No data loss
✅ Backward compatible

---

**Quick Help**: See `MULTI_COURSE_QUICK_START.md` for detailed guide
**Full Docs**: See `INSTRUCTOR_MULTI_COURSE_COMPLETE.md` for everything
