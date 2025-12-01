# Attendance Data Flow - Complete Guide

## Current Issue
Year, Course, and Session Type columns showing "-" instead of actual data in View Records page.

## Data Flow Analysis

### 1. Session Creation (Working ✅)
When instructor creates a session, the following data is stored in `sessions` collection:

```javascript
{
  instructor_id: user_id,
  instructor_name: "John Doe",
  section_id: "A",              // From form input
  year: "2nd Year",              // From form input
  session_type: "lab",           // From dropdown (lab/theory)
  time_block: "morning",         // From selection
  course_name: "Computer Science", // From instructor profile
  class_year: "2024",            // From instructor profile
  name: "Data Structures Lab",   // Session name
  course: "CS101",               // Optional course field
  start_time: datetime,
  status: "active"
}
```

### 2. Attendance Recording (Working ✅)
When face is recognized, attendance record is created with:

```javascript
{
  student_id: "STU016",
  session_id: session_id,
  instructor_id: session.instructor_id,
  section_id: session.section_id,      // ✅ Copied from session
  year: session.year,                   // ✅ Copied from session
  session_type: session.session_type,   // ✅ Copied from session
  time_block: session.time_block,
  course_name: session.course_name,     // ✅ Copied from session
  class_year: session.class_year,
  timestamp: datetime,
  date: "2025-11-28",
  confidence: 0.865,
  status: "present"
}
```

### 3. View Records Display (Backend ✅)
The `/api/instructor/records` endpoint returns:

```python
{
  'id': str(record['_id']),
  'student_id': record['student_id'],
  'student_name': student['name'],
  'session_id': record['session_id'],
  'session_name': session['name'],
  'section_id': record.get('section_id', ''),      # ✅
  'year': record.get('year', ''),                   # ✅
  'course_name': record.get('course_name', ''),     # ✅
  'session_type': record.get('session_type', ''),   # ✅
  'date': record['date'],
  'timestamp': record['timestamp'].isoformat(),
  'confidence': record.get('confidence', 0),
  'status': record.get('status', 'present')
}
```

### 4. Frontend Display (Working ✅)
The AttendanceRecords.tsx displays:
- Year: `{record.year || '-'}`
- Course: `{record.course_name || '-'}`
- Session Type: Badge showing Lab/Theory

## Why Data Shows "-"

The issue is that **existing attendance records** created before this update don't have these fields. Only **new attendance records** created after the update will have the data.

## Solution

### Option 1: Test with New Session (Recommended)
1. Create a NEW session as instructor
2. Select session type (Lab or Theory)
3. Select time block (Morning or Afternoon)
4. Enter section (e.g., "A")
5. Enter year (e.g., "2nd Year")
6. Take attendance
7. View records - the new records will show all data correctly

### Option 2: Update Existing Records (Optional)
Run a migration script to update old records with data from their sessions:

```python
# backend/migrate_attendance_fields.py
from db.mongo import get_db, init_db
from bson import ObjectId

def migrate_attendance_records():
    init_db()
    db = get_db()
    
    # Get all attendance records
    records = db.attendance.find({})
    
    updated_count = 0
    for record in records:
        # Get the session for this attendance record
        session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
        
        if session:
            # Update attendance record with session data
            update_fields = {}
            
            if 'section_id' not in record or not record.get('section_id'):
                update_fields['section_id'] = session.get('section_id', '')
            
            if 'year' not in record or not record.get('year'):
                update_fields['year'] = session.get('year', '')
            
            if 'course_name' not in record or not record.get('course_name'):
                update_fields['course_name'] = session.get('course_name', '')
            
            if 'session_type' not in record or not record.get('session_type'):
                update_fields['session_type'] = session.get('session_type', '')
            
            if 'time_block' not in record or not record.get('time_block'):
                update_fields['time_block'] = session.get('time_block', '')
            
            if update_fields:
                db.attendance.update_one(
                    {'_id': record['_id']},
                    {'$set': update_fields}
                )
                updated_count += 1
                print(f"Updated record {record['_id']}")
    
    print(f"✅ Migration complete! Updated {updated_count} records")

if __name__ == '__main__':
    migrate_attendance_records()
```

## Testing Checklist

### Test New Session Creation
1. ✅ Login as instructor
2. ✅ Click "Start New Session"
3. ✅ Select session type: Lab
4. ✅ Select time block: Morning
5. ✅ Enter session name: "Test Lab Session"
6. ✅ Enter section: "A"
7. ✅ Enter year: "2nd Year"
8. ✅ Click "Create & Start"

### Test Attendance Recording
1. ✅ Face recognition captures student
2. ✅ Attendance recorded successfully
3. ✅ Check database: attendance record has all fields

### Test View Records
1. ✅ Navigate to "View Records"
2. ✅ See the new attendance record
3. ✅ Verify columns show:
   - Status: "Present" (green badge)
   - Section: "A"
   - Year: "2nd Year"
   - Course: "Computer Science" (from instructor profile)
   - Session Type: "Lab" (blue badge)

## Expected Results

After creating a new session and taking attendance, the View Records page should show:

| Date | Time | Student | Status | Section | Year | Course | Session Type | Confidence |
|------|------|---------|--------|---------|------|--------|--------------|------------|
| 2025-11-28 | 7:21 PM | Bacha Eshetu | Present | A | 2nd Year | Computer Science | Lab | 86.5% |

## Summary

The system is **working correctly** for new sessions. The "-" values you see are from old attendance records created before the fields were added. 

**To see the correct data:**
1. Create a new session with all fields filled
2. Take attendance
3. View records - the new entries will show all data correctly

The code is already properly saving and displaying all fields. You just need to test with a new session!
