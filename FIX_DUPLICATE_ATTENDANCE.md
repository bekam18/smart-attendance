# Fix Duplicate Attendance Records

## Problem

Student "Bekam Ayele" (STU013) appears 3 times in one session:
- 12:01:46 PM - 74.0%
- 12:01:44 PM - 76.5%
- 12:01:44 PM - 60.3%

This violates the rule: **One student = One attendance entry per session**

## Root Cause

Old duplicate records exist in the database from before the duplicate prevention logic was implemented.

## Solution (3 Steps)

### Step 1: Clean Up Existing Duplicates

Run the cleanup script to remove old duplicate records:

```bash
cleanup_duplicates.bat
```

This will:
1. Find all duplicate attendance records
2. Keep only the LATEST entry for each student per session
3. Delete older duplicate entries
4. Update session attendance counts

**Example Output:**
```
⚠️  DUPLICATE FOUND:
   Student: STU013
   Session: 67890abcdef
   Date: 2024-01-15
   Count: 3 entries
   ✅ KEEPING: 12:01:46 PM (latest)
   ❌ DELETING: 12:01:44 PM
   ❌ DELETING: 12:01:44 PM

✅ Deleted 2 duplicate records
```

### Step 2: Add Database Unique Index

Run the index script to prevent future duplicates at database level:

```bash
add_unique_index.bat
```

This creates a unique compound index on `(student_id, session_id, date)`.

**Note:** If you get a "duplicate key" error, run Step 1 first!

### Step 3: Verify Fix

1. Restart the backend server
2. Start a new attendance session
3. Recognize the same student multiple times
4. Verify only ONE entry appears in the attendance list

## Technical Details

### Backend Code (Already Fixed)

The attendance recording logic in `backend/blueprints/attendance.py` now:

1. **Checks for existing entry:**
```python
existing = db.attendance.find_one({
    'student_id': student_id,
    'session_id': session_id,
    'date': today
})
```

2. **If exists, UPDATE only:**
```python
if existing:
    db.attendance.update_one(
        {'_id': existing['_id']},
        {'$set': {
            'timestamp': datetime.utcnow(),
            'confidence': confidence
        }}
    )
    return "already_marked"
```

3. **If new, INSERT:**
```python
else:
    db.attendance.insert_one(attendance_doc)
    return "recognized"
```

### Database Index

The unique index ensures MongoDB rejects duplicate inserts:

```javascript
db.attendance.createIndex(
  {
    student_id: 1,
    session_id: 1,
    date: 1
  },
  {
    unique: true,
    name: "unique_attendance_per_session"
  }
)
```

## Verification

### Check for Duplicates

Run this in MongoDB shell or Compass:

```javascript
db.attendance.aggregate([
  {
    $group: {
      _id: {
        student_id: "$student_id",
        session_id: "$session_id",
        date: "$date"
      },
      count: { $sum: 1 },
      records: { $push: "$$ROOT" }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
])
```

Should return empty array (no duplicates).

### Check Index

```javascript
db.attendance.getIndexes()
```

Should show `unique_attendance_per_session` index.

## Expected Behavior After Fix

### First Recognition
```
Student: Bekam Ayele (STU013)
Time: 12:01:44 PM
Confidence: 76.5%
Status: ✅ NEW entry created
```

### Second Recognition (same session)
```
Student: Bekam Ayele (STU013)
Time: 12:01:46 PM
Confidence: 74.0%
Status: ⚠️ Already marked (timestamp updated)
```

### Attendance List
```
Bekam Ayele
STU013
12:01:46 PM (latest timestamp)
74.0% (latest confidence)
```

Only ONE entry appears!

## Troubleshooting

### Issue: Cleanup script shows no duplicates but UI shows duplicates

**Solution:** The duplicates might be in different sessions or dates. Check:
```javascript
db.attendance.find({ student_id: "STU013" }).sort({ timestamp: -1 })
```

### Issue: "Duplicate key error" when adding index

**Solution:** Run cleanup script first:
```bash
cleanup_duplicates.bat
```

Then run index script:
```bash
add_unique_index.bat
```

### Issue: Still seeing duplicates after fix

**Possible causes:**
1. Backend server not restarted
2. Old session still using cached code
3. Multiple backend instances running

**Solution:**
1. Stop all backend processes
2. Restart backend: `cd backend && python app.py`
3. Start new attendance session
4. Test again

## Files Created

1. `backend/cleanup_duplicate_attendance.py` - Cleanup script
2. `cleanup_duplicates.bat` - Windows batch file
3. `backend/add_unique_index.py` - Index creation script
4. `add_unique_index.bat` - Windows batch file
5. `FIX_DUPLICATE_ATTENDANCE.md` - This guide

## Quick Fix Commands

```bash
# 1. Clean up duplicates
cleanup_duplicates.bat

# 2. Add unique index
add_unique_index.bat

# 3. Restart backend
cd backend
python app.py
```

## Prevention

With the fix in place:
- ✅ Backend checks for existing entries
- ✅ Database rejects duplicate inserts
- ✅ Only timestamps are updated on repeat recognition
- ✅ Attendance counts remain accurate

---

**Status**: Ready to fix
**Run**: `cleanup_duplicates.bat` then `add_unique_index.bat`
