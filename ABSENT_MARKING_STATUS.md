# Automatic Absent Marking - Status

## Current Status: ⚪ NOT IMPLEMENTED

The automatic absent marking feature described in `ABSENT_MARKING_QUICK_GUIDE.md` is **not yet implemented**. This is a planned feature for future development.

## What the Feature Would Do

When an instructor ends a session, the system would automatically:
1. Find all students registered in the session's section and year
2. Check which students were marked present during the session
3. Mark all remaining students as absent
4. Update attendance records with "absent" status

## Current Behavior

**What Happens Now:**
- Instructor starts session
- Students appear on camera → Marked as PRESENT
- Instructor ends session
- **Only present students have records** ❌
- Absent students have no attendance record

**What's Missing:**
- No automatic absent marking
- No complete attendance records
- No absent status in database

## Proposed Implementation

### Backend Changes Needed:

1. **Update `end_session` endpoint** (`backend/blueprints/attendance.py`):
```python
@attendance_bp.route('/end-session', methods=['POST'])
def end_session():
    # ... existing code ...
    
    # NEW: Mark absent students
    session = get_session(session_id)
    
    # Get all students in section/year
    all_students = db.execute_query(
        'SELECT student_id FROM students WHERE section = %s AND year = %s',
        (session['section_id'], session['year'])
    )
    
    # Get present students
    present_students = db.execute_query(
        'SELECT DISTINCT student_id FROM attendance WHERE session_id = %s',
        (session_id,)
    )
    
    # Mark absent students
    for student in all_students:
        if student['student_id'] not in present_students:
            db.execute_query(
                '''INSERT INTO attendance 
                   (student_id, session_id, instructor_id, timestamp, date, status) 
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (student['student_id'], session_id, instructor_id, 
                 datetime.utcnow(), today, 'absent')
            )
```

2. **Update attendance table** to support "absent" status:
   - Already has `status ENUM('present', 'absent')` ✅

3. **Update frontend** to display absent status:
   - Show red badges for absent students
   - Include absent students in attendance list

### Frontend Changes Needed:

1. **AttendanceSession.tsx**:
   - Display absent students in attendance list
   - Show red badge for absent status

2. **AttendanceRecords.tsx**:
   - Filter by present/absent status
   - Show status badges (green/red)

## Why Not Implemented Yet

This feature requires:
- ✅ Database schema support (already has status field)
- ⚪ Backend logic to find all students in section/year
- ⚪ Backend logic to mark absent students
- ⚪ Frontend UI to display absent students
- ⚪ Testing to ensure accuracy

## Workaround

**Current Solution:**
- Instructors can manually track absent students
- Export present students list
- Compare with class roster manually

## Future Implementation

To implement this feature:

1. **Phase 1: Backend**
   - Add absent marking logic to `end_session` endpoint
   - Query students by section/year
   - Create absent attendance records

2. **Phase 2: Frontend**
   - Update attendance list to show absent students
   - Add status badges (green/red)
   - Update filters to include absent status

3. **Phase 3: Testing**
   - Test with various section/year combinations
   - Verify absent students are marked correctly
   - Ensure no duplicate records

## Related Files

- **Guide**: `ABSENT_MARKING_QUICK_GUIDE.md` (describes how it should work)
- **Complete Doc**: `ABSENT_MARKING_COMPLETE.md` (if exists)
- **Backend**: `backend/blueprints/attendance.py` (needs implementation)
- **Frontend**: `frontend/src/pages/AttendanceSession.tsx` (needs updates)

## Decision

**Options:**

1. **Implement Now** - Add the feature with backend and frontend changes
2. **Implement Later** - Keep as planned feature for future release
3. **Skip Feature** - Current behavior (only present records) is sufficient

**Recommendation:** This is a nice-to-have feature but not critical. The current system works well for tracking present students. Absent marking can be added in a future update if needed.

---

**Date**: December 3, 2025
**Status**: ⚪ Not Implemented
**Priority**: Low (Enhancement)
**Complexity**: Medium

The absent marking feature is documented but not yet implemented. The current system focuses on tracking present students only.
