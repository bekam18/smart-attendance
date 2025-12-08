# Stop Camera & Session Management - Visual Guide

## Quick Reference

### Three Session Actions

| Action | Button | What It Does | Can Reopen? |
|--------|--------|--------------|-------------|
| **Stop Camera** | 🟠 Orange | Ends session for the day, marks absent students | ✅ Yes (after 12 hours) |
| **End Session** | 🔴 Red | Permanently ends session for semester | ❌ No |
| **Reopen Session** | 🟢 Green | Reactivates stopped session | - |

---

## 1. Stop Camera (Daily End)

### When to Use
- End of class for the day
- Want to retake attendance tomorrow
- Need to mark absent students

### How It Works
```
Active Session → Stop Camera → Marks Absent → Stopped (Daily) → Wait 12h → Can Reopen
```

### Steps
1. **During Active Session:**
   - Click "Stop Camera" button (orange)
   - Confirm: "Stop camera and mark absent students?"

2. **What Happens:**
   - ✅ All students not present are marked absent
   - ✅ Session status changes to "🟠 Stopped (Daily)"
   - ✅ Camera stops
   - ✅ Returns to dashboard

3. **After 12 Hours:**
   - Session shows "🔄 Reopen Session" button
   - Click to reactivate session
   - Old attendance records preserved

### Visual Flow
```
┌─────────────────┐
│  Active Session │
│   🟢 Camera On  │
└────────┬────────┘
         │
         │ Click "Stop Camera"
         ▼
┌─────────────────┐
│ Stopped (Daily) │
│  🟠 Wait 12h    │
└────────┬────────┘
         │
         │ After 12 hours
         ▼
┌─────────────────┐
│ Can Reopen Now  │
│  🔄 Click Here  │
└────────┬────────┘
         │
         │ Click "Reopen"
         ▼
┌─────────────────┐
│  Active Again   │
│   🟢 Camera On  │
└─────────────────┘
```

---

## 2. End Session (Semester End)

### When to Use
- Semester is ending
- Course is complete
- No more attendance needed

### How It Works
```
Active Session → End Session → Ended (Semester) → Cannot Reopen
```

### Steps
1. **During Active Session:**
   - Click "End Session" button (red)
   - Confirm: "End this session permanently for the semester? This cannot be undone."

2. **What Happens:**
   - ✅ Session status changes to "🔴 Ended (Semester)"
   - ✅ Cannot be reopened
   - ✅ Attendance records preserved
   - ✅ Returns to dashboard

### Visual Flow
```
┌─────────────────┐
│  Active Session │
│   🟢 Camera On  │
└────────┬────────┘
         │
         │ Click "End Session"
         ▼
┌─────────────────┐
│ Ended (Semester)│
│  🔴 Permanent   │
└─────────────────┘
         │
         │ Cannot Reopen
         ▼
      [FINAL]
```

---

## 3. Reopen Session (12-Hour Retake)

### When Available
- Session is in "Stopped (Daily)" status
- 12 or more hours have passed since stopping

### How It Works
```
Stopped (Daily) → Wait 12h → Reopen Button Appears → Click → Active Again
```

### Steps
1. **Check Dashboard:**
   - Look for sessions with "🟠 Stopped (Daily)" status
   - If 12+ hours passed: Shows "🔄 Reopen Session" button
   - If less than 12 hours: Shows "⏳ Reopen in X.Xh"

2. **Reopen Session:**
   - Click "🔄 Reopen Session" button
   - Confirm: "Reopen this session for attendance?"
   - Session becomes active

3. **What Happens:**
   - ✅ Session status changes to "🟢 Active"
   - ✅ Camera can be used again
   - ✅ Old attendance records preserved
   - ✅ New attendance can be taken

### Visual Flow
```
┌─────────────────────────────────────────────────────┐
│              Stopped Session Timeline               │
└─────────────────────────────────────────────────────┘

Hour 0: Stop Camera
  │
  │  ⏳ Reopen in 12.0h
  ▼
Hour 6: Still Waiting
  │
  │  ⏳ Reopen in 6.0h
  ▼
Hour 12: Can Reopen!
  │
  │  🔄 Reopen Session (button appears)
  ▼
Click Reopen
  │
  │  ✅ Session Active
  ▼
Take Attendance Again
```

---

## Dashboard Status Indicators

### Session Status Badges

| Badge | Status | Meaning | Actions Available |
|-------|--------|---------|-------------------|
| 🟢 Active | Session running | Camera is on, taking attendance | Stop Camera, End Session |
| 🟠 Stopped (Daily) | Waiting to reopen | Stopped for the day | Reopen (after 12h), View Details |
| 🔴 Ended (Semester) | Permanently closed | Cannot be reopened | View Details only |
| ⏳ Reopen in X.Xh | Countdown active | Waiting for 12 hours | View Details only |

---

## Attendance Records

### How Records Are Stored

```
┌──────────────────────────────────────────────────┐
│              Attendance Database                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  Day 1 (Dec 6):                                 │
│    - Student A: Present (9:00 AM)               │
│    - Student B: Present (9:15 AM)               │
│    - Student C: Absent                          │
│                                                  │
│  [Session Stopped - Wait 12 hours]              │
│                                                  │
│  Day 2 (Dec 7):                                 │
│    - Student A: Present (9:05 AM)               │
│    - Student C: Present (9:20 AM)               │
│    - Student B: Absent                          │
│                                                  │
│  [Session Stopped - Wait 12 hours]              │
│                                                  │
│  Day 3 (Dec 8):                                 │
│    - Student A: Present (9:10 AM)               │
│    - Student B: Present (9:25 AM)               │
│    - Student C: Present (9:30 AM)               │
│                                                  │
└──────────────────────────────────────────────────┘

✅ All records are PERMANENT
✅ Reports show complete history
✅ No data is lost when reopening
```

---

## Common Scenarios

### Scenario 1: Daily Lab Sessions
```
Monday:
  1. Start session at 8:30 AM
  2. Take attendance until 12:00 PM
  3. Click "Stop Camera"
  4. Students marked: 25 present, 5 absent

Tuesday (after 12 hours):
  1. Click "🔄 Reopen Session"
  2. Take attendance again
  3. Students marked: 28 present, 2 absent
  4. Click "Stop Camera"

Wednesday (after 12 hours):
  1. Click "🔄 Reopen Session"
  2. Take attendance again
  3. Students marked: 30 present, 0 absent
  4. Click "End Session" (semester end)

Result: Complete attendance history for all 3 days
```

### Scenario 2: Forgot to Take Attendance
```
Problem:
  - Instructor forgot to take attendance on Monday
  - Session was stopped

Solution:
  1. Wait 12 hours
  2. Click "🔄 Reopen Session"
  3. Take attendance now
  4. Old records preserved
  5. New attendance added
```

### Scenario 3: Technical Issues
```
Problem:
  - Camera not working during session
  - Need to retake attendance

Solution:
  1. Click "Stop Camera" to end current session
  2. Wait 12 hours
  3. Click "🔄 Reopen Session"
  4. Take attendance with working camera
```

---

## Testing the Feature

### Quick Test (Without Waiting 12 Hours)

1. **Start Test Session:**
   ```bash
   # Login to system as instructor
   # Start a new session
   ```

2. **Stop Camera:**
   ```bash
   # Click "Stop Camera" button
   # Verify status changes to "🟠 Stopped (Daily)"
   ```

3. **Manually Update Database (for testing):**
   ```sql
   -- Connect to MySQL
   mysql -u root -p smart_attendance
   
   -- Update end_time to 13 hours ago
   UPDATE sessions 
   SET end_time = DATE_SUB(NOW(), INTERVAL 13 HOUR) 
   WHERE id = <session_id>;
   ```

4. **Refresh Dashboard:**
   ```bash
   # Refresh browser (Ctrl+F5)
   # Should now show "🔄 Reopen Session" button
   ```

5. **Reopen Session:**
   ```bash
   # Click "🔄 Reopen Session"
   # Verify status changes to "🟢 Active"
   ```

---

## Troubleshooting

### Issue: Cannot see "Reopen" button
**Causes:**
- Less than 12 hours have passed
- Session status is not "stopped_daily"
- Page needs refresh

**Solutions:**
1. Check countdown timer: "⏳ Reopen in X.Xh"
2. Wait for countdown to reach 0
3. Refresh page (Ctrl+F5)
4. Check session status in database

### Issue: "Too soon" error when reopening
**Cause:** 12 hours have not passed yet

**Solution:**
- Wait for the remaining time shown in error message
- Or manually update database for testing (see above)

### Issue: Old attendance not showing
**Cause:** Query might be filtering by date

**Solution:**
- Check that reports include all dates
- Verify attendance records exist in database:
  ```sql
  SELECT * FROM attendance WHERE session_id = <id> ORDER BY timestamp DESC;
  ```

---

## Summary

✅ **Stop Camera** = Daily end, can reopen after 12 hours
✅ **End Session** = Permanent end, cannot reopen
✅ **Reopen Session** = Reactivate after 12 hours
✅ **All attendance records** = Permanently stored
✅ **Multiple retakes** = Supported with full history

---

## Need Help?

- Check `TIME_BLOCK_SESSIONS_COMPLETE.md` for technical details
- Run `test_session_management.py` to test endpoints
- Contact system administrator for database issues
