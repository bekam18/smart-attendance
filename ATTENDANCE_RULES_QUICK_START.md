# Attendance Recording Rules - Quick Start Guide

## What Changed?

The system now enforces strict attendance recording rules to prevent duplicates and ensure data integrity.

## Core Rule

**One student = One attendance entry per session**

When a student is recognized multiple times in the same session:
- ✅ First time: Creates new attendance record
- ✅ Subsequent times: Updates timestamp only (no new record)

## How It Works

### Scenario Example

**Session: CS101 Lab - Morning**

1. **9:05 AM - Alice arrives**
   - System creates NEW attendance entry
   - Session count: 1
   - Response: "Attendance recorded for Alice Brown"

2. **9:10 AM - Bob arrives**
   - System creates NEW attendance entry
   - Session count: 2
   - Response: "Attendance recorded for Bob Smith"

3. **9:15 AM - Alice walks past camera again**
   - System finds existing entry
   - Updates timestamp only (no new entry)
   - Session count: 2 (unchanged)
   - Response: "Alice Brown already marked present (timestamp updated)"

## API Response Differences

### New Entry
```json
{
  "status": "recognized",
  "message": "Attendance recorded for Alice Brown",
  "new_entry": true
}
```

### Already Marked
```json
{
  "status": "already_marked",
  "message": "Alice Brown already marked present (timestamp updated)",
  "updated": true
}
```

## Database Changes

### New Columns Added

**Attendance Table:**
- `year` - Student's year level
- `time_block` - Session time (morning/afternoon)

**Sessions Table:**
- `year` - Target year level
- `time_block` - Session time (morning/afternoon)

## Testing

Run the verification script:
```bash
verify_attendance_rules.bat
```

Or test individually:
```bash
# Test attendance rules
python test_attendance_rules.py

# Check database schema
python check_attendance_schema.py
python check_sessions_schema.py
```

## Benefits

✅ No duplicate attendance entries
✅ Accurate attendance counts
✅ Latest timestamp always recorded
✅ Clean, reliable data for reports

## Status

✅ **IMPLEMENTED AND TESTED**

All attendance recording rules are active and working correctly.

---

For detailed technical information, see `ATTENDANCE_RECORDING_RULES.md`
For implementation details, see `ATTENDANCE_RULES_APPLIED.md`
