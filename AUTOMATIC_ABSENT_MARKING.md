# Automatic Absent Marking Feature

## Overview

The SmartAttendance system now automatically marks students as **absent** when an instructor ends a session if they did not appear on camera during that session.

## How It Works

### 1. Session Creation
When an instructor starts a session, they specify:
- **Section** (A, B, C, or D)
- **Year** (1st Year, 2nd Year, 3rd Year, or 4th Year)
- **Course** (from their assigned courses)
- **Session Type** (Lab or Theory)
- **Time Block** (Morning or Afternoon)

### 2. During the Session
- Students appear on camera
- Face recognition identifies them
- System records attendance with status: **"present"**
- Only students who appear on camera get marked as present

### 3. Ending the Session
When the instructor clicks "End Session":

1. **System queries all students** in the selected section and year
2. **Identifies present students** from attendance records
3. **Calculates absent students** (students in section who weren't marked present)
4. **Automatically creates absent records** for each absent student with:
   - `status: "absent"`
   - `confidence: 0.0`
   - All session details (section, year, course, etc.)

### 4. Viewing Records
Both instructors and admins can view attendance records showing:
- **Present** students (green badge)
- **Absent** students (red badge)

## Example Scenario

### Section A, 4th Year has 10 students:
- STU001 - Abebe Kebede
- STU002 - Tigist Haile
- STU003 - Dawit Tesfaye
- STU004 - Meron Tadesse
- STU005 - Yonas Bekele
- STU006 - Sara Alemayehu
- STU007 - Daniel Girma
- STU008 - Hanna Mulugeta
- STU009 - Elias Tesfaye
- STU010 - Bethlehem Hailu

### During Session:
Only 3 students appear on camera:
- STU001 ✓ (marked present)
- STU003 ✓ (marked present)
- STU007 ✓ (marked present)

### When Session Ends:
System automatically marks 7 students as absent:
- STU002 ✗ (marked absent)
- STU004 ✗ (marked absent)
- STU005 ✗ (marked absent)
- STU006 ✗ (marked absent)
- STU008 ✗ (marked absent)
- STU009 ✗ (marked absent)
- STU010 ✗ (marked absent)

### Final Result:
- **Present**: 3 students
- **Absent**: 7 students
- **Total**: 10 students (complete attendance record)

## Benefits

1. **Complete Records**: No missing attendance data
2. **Automatic**: No manual marking required
3. **Accurate**: Based on actual camera appearance
4. **Section-Specific**: Only marks students from the selected section
5. **Audit Trail**: Clear distinction between present and absent

## Technical Details

### Backend Implementation
File: `backend/blueprints/attendance.py`

```python
@attendance_bp.route('/end-session', methods=['POST'])
def end_session():
    # 1. Get session details (section, year)
    # 2. Query all students in that section/year
    # 3. Find students marked present
    # 4. Calculate absent students
    # 5. Create absent records for each
    # 6. Update session status to 'completed'
```

### Database Schema
Attendance records include:
```json
{
  "student_id": "STU001",
  "session_id": "...",
  "status": "present" | "absent",
  "confidence": 0.75,  // 0.0 for absent
  "section_id": "A",
  "year": "4th Year",
  "date": "2025-12-01",
  "timestamp": "2025-12-01T10:30:00Z"
}
```

### Frontend Display
- **Instructor Dashboard**: View records with status badges
- **Admin Dashboard**: View all records with status column
- **Export**: CSV/Excel exports include status field

## Testing

Run the test script to verify the feature:

```bash
test_absent_marking.bat
```

This will:
1. Login as instructor
2. Start a session for a specific section
3. Simulate some students appearing
4. End the session
5. Verify absent students are marked

## API Response

When ending a session, the API returns:

```json
{
  "message": "Session ended successfully",
  "present_count": 3,
  "absent_count": 7,
  "total_students": 10
}
```

## Important Notes

1. **Section-Based**: Only students in the selected section are considered
2. **No Duplicates**: System checks for existing records before creating absent entries
3. **Timestamp**: Absent records get the session end time as timestamp
4. **Confidence**: Absent records have 0.0 confidence (no face detected)
5. **Immutable**: Once marked, records are permanent (no auto-updates)

## User Guide

### For Instructors

1. **Start Session**
   - Select your section (A, B, C, or D)
   - Select year level (1st-4th Year)
   - Choose course and session type
   - Click "Start Session"

2. **During Session**
   - Students appear on camera
   - System automatically recognizes and marks them present
   - You can see live count of present students

3. **End Session**
   - Click "End Session" button
   - System automatically marks absent students
   - View summary: X present, Y absent, Z total

4. **View Records**
   - Go to "Attendance Records" page
   - Filter by date, session, or student
   - See status badges (green = present, red = absent)
   - Export to CSV or Excel

### For Admins

1. **View All Records**
   - Access "All Records" page
   - Filter by section, instructor, date
   - See complete attendance with status column
   - Export filtered data

2. **Monitor Attendance**
   - Check attendance rates per section
   - Identify students with frequent absences
   - Generate reports for analysis

## Troubleshooting

### Issue: No absent students marked
**Solution**: Ensure students are in the database with correct section and year

### Issue: Wrong students marked absent
**Solution**: Verify session section/year matches student records

### Issue: Duplicate absent records
**Solution**: System prevents duplicates automatically; check logs if occurring

## Future Enhancements

Possible improvements:
- Email notifications to absent students
- Attendance rate calculations
- Absence pattern analysis
- Excuse/reason for absence field
- Late arrival tracking

## Related Documentation

- [Instructor Multi-Course Feature](INSTRUCTOR_MULTI_COURSE_SECTION_FEATURE.md)
- [Section and Year Management](SECTION_YEAR_QUICK_GUIDE.md)
- [Attendance Recording Rules](ATTENDANCE_RECORDING_RULES.md)
- [API Documentation](API_DOCUMENTATION.md)
