# Multi-Course Instructor - Quick Start Guide

## What's New?

Instructors can now teach **multiple courses** instead of just one!

## Quick Setup

### 1. Migrate Existing Data (One-Time)

```bash
migrate_instructor_courses.bat
```

This converts existing instructors to the new format.

### 2. Start Using

That's it! The feature is ready to use.

## How to Use

### Adding an Instructor with Multiple Courses

1. **Login as Admin**
2. **Click "Add Instructor"**
3. **Fill in basic info** (username, email, name, etc.)
4. **Add courses:**
   - Type course name
   - Press **Enter** or click **"Add Course"**
   - Repeat for each course
5. **Remove courses** by clicking the **×** button
6. **Select session types** (Lab/Theory)
7. **Click "Add Instructor"**

### Example

```
Name: Dr. Sarah Johnson
Courses:
  ✓ Data Structures
  ✓ Algorithms  
  ✓ Database Systems
Year: 3rd Year
Sessions: Lab + Theory
```

## Visual Guide

### Before (Single Course)
```
Course Name: [Data Structures        ]
```

### After (Multiple Courses)
```
Courses:
┌─────────────────────────────────────┐
│ [Data Structures ×]                 │
│ [Algorithms ×]                      │
│ [Database Systems ×]                │
│                                     │
│ [Type course name...] [Add Course]  │
│ 3 course(s) added                   │
└─────────────────────────────────────┘
```

## Instructor Table Display

Courses now show as multiple badges:

```
┌──────────────┬────────────────────────────┐
│ Name         │ Courses                    │
├──────────────┼────────────────────────────┤
│ Dr. Johnson  │ [Data Structures]          │
│              │ [Algorithms]               │
│              │ [Database Systems]         │
└──────────────┴────────────────────────────┘
```

## Tips

💡 **Press Enter** to quickly add courses
💡 **Click ×** to remove a course
💡 **At least 1 course** is required
💡 **Old instructors** still work (backward compatible)

## Troubleshooting

### "At least one course is required" error
- Make sure you've added at least one course before submitting

### Courses not showing
- Run the migration script: `migrate_instructor_courses.bat`
- Refresh the page

### Old instructors not displaying
- The system automatically converts old format to new format
- No action needed

## API Format

### Request Body
```json
{
  "username": "dr.johnson",
  "password": "password123",
  "email": "johnson@university.edu",
  "name": "Dr. Sarah Johnson",
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

## Benefits

✅ More realistic teaching assignments
✅ Better flexibility
✅ Easy to manage
✅ Works with existing data

---

**Need Help?** See `INSTRUCTOR_MULTI_COURSE_COMPLETE.md` for full documentation.
