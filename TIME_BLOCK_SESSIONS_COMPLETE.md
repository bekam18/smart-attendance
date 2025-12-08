# Session Management with 12-Hour Retake Feature - Complete Implementation

## Overview
Implemented comprehensive session management system with three key features:
1. **Retake Attendance after 12 hours** - Reopen sessions while preserving old records
2. **Stop Camera (Daily End)** - End session for the day, can be reopened
3. **End Session (Semester End)** - Permanently close session

## Features Implemented

### 1. Session Status Types
Sessions now have three distinct statuses:
- **`active`** - Session is currently running, camera is on
- **`stopped_daily`** - Session stopped for the day, can be reopened after 12 hours
- **`ended_semester`** - Session permanently ended for semester (cannot be reopened)

### 2. Stop Camera (Daily End)
**What it does:**
- Marks all absent students who didn't attend
- Stops the camera and ends session for the day
- Sets session status to `stopped_daily`
- Can be reopened after 12 hours

**How to use:**
1. During an active session, click "Stop Camera" button
2. Confirms action with user
3. Marks absent students automatically
4. Navigates back to dashboard
5. Session shows as "🟠 Stopped (Daily)" with countdown timer

**Backend Endpoint:** `POST /api/attendance/mark-absent`
```python
# Marks absent students AND stops session for the day
db.execute_query(
    'UPDATE sessions SET end_time = %s, status = %s WHERE id = %s',
    (datetime.utcnow(), 'stopped_daily', session_id)
)
```

### 3. End Session (Semester End)
**What it does:**
- Permanently ends the session for the semester
- Cannot be reopened
- Sets session status to `ended_semester`

**How to use:**
1. During an active session, click "End Session" button
2. Confirms with warning: "End this session permanently for the semester? This cannot be undone."
3. Session shows as "🔴 Ended (Semester)"

**Backend Endpoint:** `POST /api/attendance/end-session`
```json
{
  "session_id": "123",
  "end_type": "semester"  // or "daily"
}
```

### 4. Reopen Session (12-Hour Retake)
**What it does:**
- Allows instructors to reopen sessions after 12 hours
- Previous attendance records are preserved permanently in database
- New attendance can be taken
- Attendance list shows current session's attendance (temporary display)

**How to use:**
1. After 12 hours, session shows "🔄 Reopen Session" button
2. Before 12 hours, shows countdown: "⏳ Reopen in X.Xh"
3. Click "Reopen Session" to reactivate
4. Session becomes active again, camera can be used

**Backend Endpoint:** `POST /api/attendance/reopen-session`
```python
# Check if 12 hours have passed
hours_since_stop = (datetime.utcnow() - end_time).total_seconds() / 3600
if hours_since_stop >= 12:
    can_reopen = True
```

**Key Logic:**
- Old attendance records remain in database permanently
- Session status changes from `stopped_daily` → `active`
- `end_time` is cleared (set to NULL)
- Attendance count continues from previous value

## Database Schema

### Sessions Table
```sql
CREATE TABLE sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    instructor_id INT,
    instructor_name VARCHAR(255),
    section_id VARCHAR(10),
    year VARCHAR(20),
    session_type ENUM('lab', 'theory'),
    time_block ENUM('morning', 'afternoon'),
    course_name VARCHAR(255),
    name VARCHAR(255),
    start_time DATETIME,
    end_time DATETIME,  -- NULL when active, set when stopped
    status ENUM('active', 'stopped_daily', 'ended_semester', 'completed'),
    attendance_count INT DEFAULT 0
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(50),
    session_id INT,
    instructor_id INT,
    section_id VARCHAR(10),
    year VARCHAR(20),
    session_type ENUM('lab', 'theory'),
    time_block ENUM('morning', 'afternoon'),
    course_name VARCHAR(255),
    timestamp DATETIME,
    date DATE,
    confidence FLOAT,
    status ENUM('present', 'absent')
);
```

**Important:** All attendance records are permanent. When a session is reopened, old records remain and new records are added.

## API Endpoints

### 1. Mark Absent (Stop Camera)
```http
POST /api/attendance/mark-absent
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "123"
}
```

**Response:**
```json
{
  "message": "Successfully marked 5 students as absent",
  "absent_count": 5,
  "total_students": 30,
  "present_count": 25
}
```

### 2. End Session
```http
POST /api/attendance/end-session
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "123",
  "end_type": "semester"  // or "daily"
}
```

**Response:**
```json
{
  "message": "Session ended permanently for semester"
}
```

### 3. Reopen Session
```http
POST /api/attendance/reopen-session
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "123"
}
```

**Response (Success):**
```json
{
  "message": "Session reopened successfully. Previous attendance records are preserved.",
  "session_id": "123"
}
```

**Response (Too Soon):**
```json
{
  "error": "Too soon",
  "message": "Session can be reopened after 12 hours. 8.5 hours remaining.",
  "hours_remaining": 8.5
}
```

### 4. Get Sessions (with reopen info)
```http
GET /api/attendance/sessions
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "123",
    "name": "lab - morning",
    "status": "stopped_daily",
    "can_reopen": true,
    "hours_until_reopen": null,
    "start_time": "2025-12-08T08:30:00",
    "end_time": "2025-12-07T20:30:00",
    "attendance_count": 25
  },
  {
    "id": "124",
    "name": "theory - afternoon",
    "status": "stopped_daily",
    "can_reopen": false,
    "hours_until_reopen": 3.5,
    "start_time": "2025-12-08T13:30:00",
    "end_time": "2025-12-08T17:00:00",
    "attendance_count": 28
  }
]
```

## Frontend Components

### Updated Files

#### 1. `frontend/src/lib/api.ts`
Added new API methods:
```typescript
attendanceAPI.endSession(sessionId, 'daily' | 'semester')
attendanceAPI.reopenSession(sessionId)
```

#### 2. `frontend/src/pages/AttendanceSession.tsx`
- Updated "Stop Camera" to confirm and show 12-hour message
- Updated "End Session" to confirm permanent action
- Both buttons navigate back to dashboard after action

#### 3. `frontend/src/pages/InstructorDashboard.tsx`
- Added `handleReopenSession()` function
- Updated session display to show:
  - "🔄 Reopen Session" button when eligible (12+ hours)
  - "⏳ Reopen in X.Xh" countdown when not yet eligible
  - Status badges: 🟢 Active, 🟠 Stopped (Daily), 🔴 Ended (Semester)

#### 4. `frontend/src/types/index.ts`
Updated Session interface:
```typescript
interface Session {
  status: 'active' | 'completed' | 'stopped_daily' | 'ended_semester';
  can_reopen?: boolean;
  hours_until_reopen?: number | null;
}
```

## User Workflow

### Scenario 1: Daily Session
1. Instructor starts session at 8:30 AM
2. Students attend throughout the morning
3. At 12:00 PM, instructor clicks "Stop Camera"
4. System marks absent students and stops session
5. Session shows "🟠 Stopped (Daily)" with countdown
6. After 12 hours (8:00 PM), "🔄 Reopen Session" button appears
7. Next day, instructor clicks "Reopen Session"
8. Session becomes active again, old attendance preserved

### Scenario 2: Semester End
1. Instructor has active session
2. Semester is ending
3. Instructor clicks "End Session"
4. Confirms permanent end
5. Session shows "🔴 Ended (Semester)"
6. Cannot be reopened

### Scenario 3: Multiple Retakes
1. Session created on Day 1, stopped after class
2. Day 2: Reopened after 12 hours, new attendance taken, stopped
3. Day 3: Reopened again, more attendance taken
4. Database has all attendance records from all days
5. Reports show complete attendance history

## Data Persistence

### Attendance Records
All attendance records are **permanent** and stored in the database:
- When session is stopped: Records remain
- When session is reopened: Old records preserved, new records added
- When generating reports: All records included

### Example Query
```sql
-- Get all attendance for a session (across multiple reopens)
SELECT * FROM attendance 
WHERE session_id = 123 
ORDER BY timestamp DESC;

-- Result shows attendance from multiple days:
-- 2025-12-08 09:00:00 - Student A - Present
-- 2025-12-07 09:15:00 - Student B - Present
-- 2025-12-06 09:30:00 - Student A - Present
```

## Testing

### Test Scenario 1: Stop and Reopen
```bash
# 1. Start session
curl -X POST http://localhost:5000/api/attendance/start-session \
  -H "Authorization: Bearer <token>" \
  -d '{"name":"Test Session","section_id":"A","year":"4th Year"}'

# 2. Stop camera (marks absent)
curl -X POST http://localhost:5000/api/attendance/mark-absent \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id":"123"}'

# 3. Try to reopen immediately (should fail)
curl -X POST http://localhost:5000/api/attendance/reopen-session \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id":"123"}'
# Response: "Too soon, 12.0 hours remaining"

# 4. Wait 12 hours or manually update end_time in database
UPDATE sessions SET end_time = DATE_SUB(NOW(), INTERVAL 13 HOUR) WHERE id = 123;

# 5. Reopen session (should succeed)
curl -X POST http://localhost:5000/api/attendance/reopen-session \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id":"123"}'
# Response: "Session reopened successfully"
```

### Test Scenario 2: Permanent End
```bash
# End session permanently
curl -X POST http://localhost:5000/api/attendance/end-session \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id":"123","end_type":"semester"}'

# Try to reopen (should fail)
curl -X POST http://localhost:5000/api/attendance/reopen-session \
  -H "Authorization: Bearer <token>" \
  -d '{"session_id":"123"}'
# Response: "Cannot reopen - Only stopped sessions can be reopened"
```

## Benefits

### For Instructors
- **Flexibility**: Can retake attendance if needed
- **Accuracy**: Multiple chances to capture attendance
- **Control**: Choose between daily stop and permanent end
- **Transparency**: Clear status indicators and countdown timers

### For Students
- **Fairness**: Multiple opportunities to be marked present
- **Accuracy**: Reduces false absences due to technical issues
- **History**: Complete attendance record across all sessions

### For System
- **Data Integrity**: All records preserved permanently
- **Audit Trail**: Complete history of when attendance was taken
- **Scalability**: Supports multiple retakes without data loss

## Files Modified

### Backend
- `backend/blueprints/attendance.py` - Added reopen endpoint, updated end-session and mark-absent

### Frontend
- `frontend/src/lib/api.ts` - Added reopenSession method, updated endSession
- `frontend/src/pages/AttendanceSession.tsx` - Updated button handlers with confirmations
- `frontend/src/pages/InstructorDashboard.tsx` - Added reopen button and status display
- `frontend/src/types/index.ts` - Updated Session interface

### Documentation
- `TIME_BLOCK_SESSIONS_COMPLETE.md` - This file

## Next Steps

### Optional Enhancements
1. **Email Notifications**: Notify instructor when session can be reopened
2. **Auto-Reopen**: Option to automatically reopen sessions daily
3. **Attendance Comparison**: Show diff between multiple retakes
4. **Session Templates**: Save session configs for quick recreation
5. **Bulk Operations**: Reopen multiple sessions at once

## Troubleshooting

### Issue: "Too soon" error when reopening
**Solution:** Wait for 12 hours to pass since session was stopped. Check `end_time` in database.

### Issue: Cannot see reopen button
**Solution:** 
1. Check session status is `stopped_daily` (not `ended_semester`)
2. Verify 12 hours have passed
3. Refresh the page to reload session data

### Issue: Old attendance not showing
**Solution:** Attendance records are permanent in database. Check query includes all dates, not just today.

### Issue: Session shows wrong status
**Solution:** Backend may need restart. Run `restart_backend.bat` or `cd backend && python app.py`

## Summary

✅ **Implemented:**
- 12-hour retake attendance feature
- Stop Camera (daily end) with absent marking
- End Session (permanent semester end)
- Reopen Session after 12 hours
- Status tracking and display
- Countdown timers
- Confirmation dialogs
- Data persistence

✅ **Tested:**
- Session stopping and reopening
- 12-hour validation
- Attendance record preservation
- Status transitions
- UI updates

✅ **Ready for Production**
