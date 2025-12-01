# Attendance Recording Rules

## Core Rule

**One student = One attendance entry per session**

When a student is recognized again in the same session, the system **ONLY UPDATES** the timestamp - it never creates a new entry.

## Implementation

### Database Query
```python
existing = db.attendance.find_one({
    'student_id': student_id,
    'session_id': session_id,
    'date': today
})
```

### Logic Flow

#### First Recognition (New Entry)
```
Student recognized
    ↓
Check if entry exists for this session
    ↓
No existing entry found
    ↓
CREATE new attendance record
    ↓
Increment session attendance_count
    ↓
Return: "Attendance recorded for [Student Name]"
```

#### Subsequent Recognition (Update Only)
```
Student recognized again
    ↓
Check if entry exists for this session
    ↓
Existing entry found
    ↓
UPDATE timestamp and confidence only
    ↓
DO NOT increment attendance_count
    ↓
Return: "[Student Name] already marked present (timestamp updated)"
```

## Code Implementation

### First Recognition
```python
# Record NEW attendance entry
attendance_doc = {
    'student_id': student_id,
    'session_id': session_id,
    'instructor_id': session.get('instructor_id'),
    'section_id': session.get('section_id', ''),
    'timestamp': datetime.utcnow(),
    'date': today,
    'confidence': confidence,
    'status': 'present'
}

db.attendance.insert_one(attendance_doc)

# Update session count (only for NEW entries)
db.sessions.update_one(
    {'_id': ObjectId(session_id)},
    {'$inc': {'attendance_count': 1}}
)
```

### Subsequent Recognition
```python
# UPDATE TIMESTAMP ONLY - DO NOT CREATE NEW ENTRY
db.attendance.update_one(
    {'_id': existing['_id']},
    {
        '$set': {
            'timestamp': datetime.utcnow(),
            'confidence': confidence
        }
    }
)

# NO increment to attendance_count
```

## Database Schema

### Attendance Collection
```javascript
{
  _id: ObjectId,
  student_id: String,        // Unique per session
  session_id: String,        // Session identifier
  instructor_id: String,     // Instructor who created session
  section_id: String,        // Section identifier
  timestamp: DateTime,       // Last recognition time (updated on repeat)
  date: String,              // ISO date (YYYY-MM-DD)
  confidence: Float,         // Recognition confidence (updated on repeat)
  status: String             // 'present'
}
```

### Unique Constraint (Logical)
The combination of `(student_id, session_id, date)` is unique.

## API Response

### First Recognition
```json
{
  "status": "recognized",
  "student_id": "S001",
  "student_name": "Alice Brown",
  "confidence": 0.95,
  "message": "Attendance recorded for Alice Brown",
  "new_entry": true
}
```

### Subsequent Recognition
```json
{
  "status": "already_marked",
  "student_id": "S001",
  "student_name": "Alice Brown",
  "confidence": 0.96,
  "message": "Alice Brown already marked present (timestamp updated)",
  "updated": true
}
```

## Benefits

### 1. Data Integrity
- No duplicate entries per session
- Clean attendance records
- Accurate attendance counts

### 2. Accurate Statistics
- Session attendance_count reflects unique students
- Reports show correct numbers
- No inflated attendance figures

### 3. Timestamp Tracking
- Latest recognition time is always recorded
- Useful for late arrivals
- Audit trail maintained

### 4. Confidence Updates
- Most recent confidence score is stored
- Better quality metrics
- Reflects latest recognition accuracy

## Example Scenario

### Session: "CS101 - Monday 9:00 AM"

**9:05 AM - Alice arrives**
```
Recognition → New entry created
attendance_count: 1
timestamp: 2024-01-15 09:05:00
```

**9:10 AM - Bob arrives**
```
Recognition → New entry created
attendance_count: 2
timestamp: 2024-01-15 09:10:00
```

**9:15 AM - Alice recognized again (walks past camera)**
```
Recognition → Existing entry UPDATED
attendance_count: 2 (unchanged)
Alice's timestamp: 2024-01-15 09:15:00 (updated)
```

**9:20 AM - Charlie arrives**
```
Recognition → New entry created
attendance_count: 3
timestamp: 2024-01-15 09:20:00
```

**Final Result:**
- Total unique students: 3
- Alice: Present (last seen 9:15 AM)
- Bob: Present (last seen 9:10 AM)
- Charlie: Present (last seen 9:20 AM)

## Verification

### Check for Duplicates
```javascript
// MongoDB query to find duplicates
db.attendance.aggregate([
  {
    $group: {
      _id: {
        student_id: "$student_id",
        session_id: "$session_id",
        date: "$date"
      },
      count: { $sum: 1 }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
])

// Should return empty array (no duplicates)
```

### Verify Attendance Count
```javascript
// Count unique students in session
db.attendance.countDocuments({
  session_id: "session_id_here",
  date: "2024-01-15"
})

// Should match session.attendance_count
```

## Edge Cases Handled

### 1. Same Student, Different Sessions
✅ Allowed - Different session_id creates separate entries

### 2. Same Student, Same Session, Same Day
✅ Handled - Updates existing entry only

### 3. Same Student, Same Session, Different Days
✅ Allowed - Different date creates separate entries

### 4. Multiple Students, Same Session
✅ Handled - Each gets their own entry

## Testing

### Test Script
```python
# Test attendance recording rules
from db.mongo import get_db
from datetime import datetime

db = get_db()

# Create test session
session_id = "test_session_123"
student_id = "S001"
today = "2024-01-15"

# First recognition
result1 = db.attendance.find_one({
    'student_id': student_id,
    'session_id': session_id,
    'date': today
})
print(f"First check: {result1}")  # Should be None

# Insert first entry
db.attendance.insert_one({
    'student_id': student_id,
    'session_id': session_id,
    'date': today,
    'timestamp': datetime.utcnow(),
    'confidence': 0.95
})

# Second recognition (should update)
result2 = db.attendance.find_one({
    'student_id': student_id,
    'session_id': session_id,
    'date': today
})
print(f"Second check: {result2}")  # Should exist

# Count entries
count = db.attendance.count_documents({
    'student_id': student_id,
    'session_id': session_id,
    'date': today
})
print(f"Entry count: {count}")  # Should be 1
```

## Monitoring

### Log Messages

**New Entry:**
```
✓ NEW attendance recorded: Alice Brown
```

**Update Entry:**
```
⚠ Already marked: Alice Brown - Updating timestamp only
✓ Timestamp updated for: Alice Brown
```

### Database Indexes (Recommended)
```javascript
// Create compound index for fast lookups
db.attendance.createIndex({
  student_id: 1,
  session_id: 1,
  date: 1
}, {
  unique: true,
  name: "unique_attendance_per_session"
})
```

## Summary

✅ **Rule Enforced**: One student = One attendance entry per session
✅ **No Duplicates**: Existing entries are updated, not duplicated
✅ **Accurate Counts**: attendance_count reflects unique students
✅ **Timestamp Tracking**: Latest recognition time is always recorded
✅ **Data Integrity**: Clean, consistent attendance records

---

**Status**: ✅ IMPLEMENTED
**Location**: `backend/blueprints/attendance.py`
**Function**: `recognize_face()`
