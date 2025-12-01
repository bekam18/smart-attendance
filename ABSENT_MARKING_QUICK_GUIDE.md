# Automatic Absent Marking - Quick Guide

## What It Does
When you end a session, students who didn't appear on camera are automatically marked as **ABSENT**.

## How to Use

### Step 1: Start Session
```
1. Select Section (A, B, C, or D)
2. Select Year (1st-4th Year)
3. Choose Course
4. Click "Start Session"
```

### Step 2: Take Attendance
```
- Students appear on camera
- System recognizes faces
- Marks them as PRESENT automatically
```

### Step 3: End Session
```
1. Click "End Session"
2. System automatically:
   ✓ Finds all students in your section
   ✓ Checks who was marked present
   ✓ Marks remaining students as ABSENT
```

### Step 4: View Records
```
- Go to "Attendance Records"
- See status badges:
  🟢 Present (green)
  🔴 Absent (red)
```

## Example

**Section A, 4th Year - 10 students total**

**During session:**
- 3 students appear on camera → Marked PRESENT

**When you end session:**
- 7 students didn't appear → Automatically marked ABSENT

**Result:**
- Present: 3 ✓
- Absent: 7 ✗
- Total: 10 (complete record)

## Key Points

✓ **Automatic** - No manual marking needed
✓ **Section-specific** - Only your section students
✓ **Complete records** - No missing data
✓ **Clear status** - Present vs Absent badges
✓ **Export ready** - CSV/Excel include status

## View Your Records

**Instructor Dashboard → Attendance Records**
- Filter by date, session, or student
- Export to CSV or Excel
- See present/absent status for all students

## Testing

Run this command to test:
```bash
test_absent_marking.bat
```

## Need Help?

See full documentation: [AUTOMATIC_ABSENT_MARKING.md](AUTOMATIC_ABSENT_MARKING.md)
