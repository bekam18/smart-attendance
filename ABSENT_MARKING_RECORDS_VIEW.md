# Absent Students in Attendance Records - Complete Guide

## Overview

When you click "Stop Camera" during a session, absent students are automatically marked. These absent students appear in the **Attendance Records** page with their section and year information.

## How It Works

### Step 1: Start Session
```
Instructor Dashboard → Start Session
- Select Section: A
- Select Year: 4th Year
- Select Course: CS101
- Click "Start Session"
```

### Step 2: Take Attendance
```
Attendance Session Page:
- Camera recognizes students
- 3 students appear → Marked PRESENT ✓
```

### Step 3: Stop Camera
```
Click "Stop Camera" button:
- System queries: All students in Section A, 4th Year
- Finds: 12 total students
- Already present: 3 students
- Marks absent: 9 students (12 - 3 = 9)
```

### Step 4: View Records
```
Instructor Dashboard → Attendance Records
- Shows all attendance records
- Includes section and year columns
- Displays present and absent students
```

## Attendance Records Display

### Table Columns:
| Date | Time | Student | Status | Section | Year | Course | Session Type | Confidence |
|------|------|---------|--------|---------|------|--------|--------------|------------|
| 2025-12-04 | 10:30 AM | Nabila (STU001) | 🟢 Present | A | 4th Year | CS101 | Lab | 95% |
| 2025-12-04 | 10:31 AM | Nardos (STU002) | 🟢 Present | A | 4th Year | CS101 | Lab | 92% |
| 2025-12-04 | 10:32 AM | Amanu (STU003) | 🟢 Present | A | 4th Year | CS101 | Lab | 88% |
| 2025-12-04 | 10:35 AM | Student 4 (STU004) | 🔴 Absent | A | 4th Year | CS101 | Lab | 0% |
| 2025-12-04 | 10:35 AM | Student 5 (STU005) | 🔴 Absent | A | 4th Year | CS101 | Lab | 0% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Key Features:

1. **Status Badge:**
   - 🟢 Green "Present" for recognized students
   - 🔴 Red "Absent" for non-present students

2. **Section Column:**
   - Shows the section (A, B, C, or D)
   - Verifies student is from correct section

3. **Year Column:**
   - Shows the year (1st, 2nd, 3rd, 4th Year)
   - Verifies student is from correct year

4. **Confidence:**
   - Present students: Shows recognition confidence (60-100%)
   - Absent students: Shows 0% (not recognized)

## Verification

### Check Section Match:
```
For each absent student in records:
1. Check student's section matches session's section
2. Check student's year matches session's year
3. Verify no students from other sections are marked
```

### Run Verification Script:
```bash
verify_absent_students_section.bat
```

This script:
- Checks all recent sessions
- Verifies absent students are from correct section
- Reports any mismatches
- Shows sample of absent students

## Example Scenario

### Database:
- **Section A, 4th Year:** 12 students
- **Section B, 4th Year:** 7 students

### Session Started:
- **Section:** A
- **Year:** 4th Year
- **Course:** CS101 Lab

### During Session:
- 3 students from Section A recognized → PRESENT

### After "Stop Camera":
- 9 students from Section A marked → ABSENT
- 0 students from Section B affected

### Attendance Records View:
```
Showing 12 records:

Present (3):
✓ STU001 - Nabila - Section A, 4th Year
✓ STU002 - Nardos - Section A, 4th Year
✓ STU003 - Amanu - Section A, 4th Year

Absent (9):
✗ STU004 - Student 4 - Section A, 4th Year
✗ STU005 - Student 5 - Section A, 4th Year
✗ STU006 - Student 6 - Section A, 4th Year
... (6 more from Section A, 4th Year)

Section B students: NOT in this list ✓
```

## Filters

### Filter by Section:
The records page doesn't have a direct section filter, but you can:
1. Filter by **Session** (each session has a section)
2. Filter by **Student** (each student has a section)
3. Use **Search** to find specific students

### Filter by Status:
Currently, the page shows all records. To see only absent students:
- Use the search/filter functionality
- Or export to Excel and filter there

## Export Features

### CSV Export:
```
Click "Export CSV" button:
- Downloads all filtered records
- Includes section and year columns
- Shows present/absent status
- Can be opened in Excel
```

### Excel Export:
```
Click "Export Excel" button:
- Downloads formatted Excel file
- Includes all columns
- Ready for analysis
- Can filter by section/status
```

## Database Structure

### Attendance Table:
```sql
CREATE TABLE attendance (
  id INT PRIMARY KEY,
  student_id VARCHAR(50),
  session_id INT,
  section_id VARCHAR(10),  -- Student's section
  year VARCHAR(20),         -- Student's year
  status VARCHAR(20),       -- 'present' or 'absent'
  timestamp DATETIME,
  confidence FLOAT,
  ...
);
```

### Query for Absent Students:
```sql
-- Get all absent students with their section info
SELECT 
  a.student_id,
  s.name as student_name,
  s.section,
  s.year,
  a.status,
  a.timestamp
FROM attendance a
JOIN students s ON a.student_id = s.student_id
WHERE a.status = 'absent'
  AND a.session_id = ?
ORDER BY s.section, s.year, s.name;
```

## Verification Checklist

✅ **Section Match:**
- [ ] Absent students are from session's section
- [ ] No students from other sections marked

✅ **Year Match:**
- [ ] Absent students are from session's year
- [ ] No students from other years marked

✅ **Display:**
- [ ] Section column shows correct section
- [ ] Year column shows correct year
- [ ] Status badge shows "Absent" in red

✅ **Export:**
- [ ] CSV includes section and year
- [ ] Excel includes all columns
- [ ] Data is accurate

## Testing Steps

### 1. Start Session:
```
- Login as instructor
- Start session for "Section A, 4th Year"
```

### 2. Take Attendance:
```
- Let 2-3 students get recognized
- Verify they show as present
```

### 3. Stop Camera:
```
- Click "Stop Camera" button
- Check success message: "Marked X students as absent"
```

### 4. View Records:
```
- Go to "Attendance Records"
- Check absent students are shown
- Verify section column shows "A"
- Verify year column shows "4th Year"
```

### 5. Verify Section:
```
- Run: verify_absent_students_section.bat
- Check output shows no mismatches
- Confirm all absent students are from Section A
```

### 6. Export:
```
- Click "Export CSV"
- Open in Excel
- Filter by Status = "Absent"
- Verify all have Section = "A", Year = "4th Year"
```

## Common Issues

### Issue: Absent students from wrong section
**Cause:** Session section doesn't match student section
**Fix:** Verify session was started with correct section

### Issue: Section column shows "-"
**Cause:** Section data not saved in attendance record
**Fix:** Check that session has section_id set

### Issue: Year column shows "-"
**Cause:** Year data not saved in attendance record
**Fix:** Check that session has year set

## Status

✅ **Implementation:** Complete
✅ **Section Filter:** Working correctly
✅ **Records Display:** Shows section and year
✅ **Export:** Includes all data
✅ **Verification:** Script available

---

**Date:** December 4, 2025
**Status:** ✅ Working Correctly

The absent marking feature correctly marks students from the session's section, and the Attendance Records page displays this information with section and year columns for verification.
