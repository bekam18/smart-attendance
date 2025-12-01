# Fix Missing Attendance Data (Year, Course, Session Type)

## Problem
The View Records page shows "-" for Year, Course, and Session Type columns instead of actual data.

## Cause
Existing attendance records were created before these fields were added to the system. The code is working correctly for NEW records, but old records don't have the data.

## Solution

### Option 1: Run Migration Script (Recommended)
This will update all existing attendance records with data from their sessions.

**Steps:**
1. Open Command Prompt
2. Navigate to project directory
3. Run: `migrate_attendance_fields.bat`
4. Wait for completion
5. Refresh the View Records page

**What it does:**
- Finds all attendance records
- Looks up their session data
- Copies year, course, session_type, section, and time_block from session to attendance record
- Updates the database

### Option 2: Test with New Session
Create a new session and take attendance to see the fields working correctly.

**Steps:**
1. Login as instructor
2. Click "Start New Session"
3. Fill in ALL fields:
   - Session Type: Lab or Theory
   - Time Block: Morning or Afternoon
   - Session Name: e.g., "Test Session"
   - Section: e.g., "A"
   - Year: e.g., "2nd Year"
4. Click "Create & Start"
5. Take attendance using face recognition
6. Go to "View Records"
7. The new record will show all data correctly

## Verification

After running the migration or creating a new session, the View Records page should show:

| Column | Expected Value | Badge Color |
|--------|---------------|-------------|
| Status | Present/Absent | Green/Red |
| Section | A, B, C, etc. | - |
| Year | 2nd Year, 3rd Year, etc. | - |
| Course | Computer Science, etc. | - |
| Session Type | Lab or Theory | Blue/Purple |

## Technical Details

### Data Flow
```
Session Creation
    ↓
Stores: session_type, time_block, section, year, course_name
    ↓
Attendance Recording
    ↓
Copies ALL session fields to attendance record
    ↓
View Records
    ↓
Displays: Status, Section, Year, Course, Session Type
```

### Database Fields

**Sessions Collection:**
- `session_type`: 'lab' or 'theory'
- `time_block`: 'morning' or 'afternoon'
- `section_id`: 'A', 'B', 'C', etc.
- `year`: '2nd Year', '3rd Year', etc.
- `course_name`: From instructor profile
- `class_year`: From instructor profile

**Attendance Collection:**
- All fields from session (copied automatically)
- Plus: `student_id`, `confidence`, `timestamp`, `status`

## Troubleshooting

### Still showing "-" after migration?
1. Check if migration completed successfully
2. Verify the session has the data (check sessions collection in database)
3. Try creating a new session and taking attendance

### Migration errors?
1. Make sure MongoDB is running
2. Check backend/.env has correct MONGODB_URI
3. Run from project root directory

### New sessions still showing "-"?
1. Make sure you filled in ALL fields when creating the session
2. Check that session_type dropdown has a value selected
3. Verify section and year fields are not empty

## Summary

✅ **The code is working correctly**
✅ **New sessions will have all data**
✅ **Run migration to fix old records**
✅ **All fields will display properly after migration**

The system is fully functional. You just need to either:
1. Run the migration script to update old records, OR
2. Create new sessions (which will automatically have all fields)
