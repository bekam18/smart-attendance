# Session Management - Quick Reference Card

## Three Actions

| Action | Button Color | Icon | When to Use | Can Reopen? |
|--------|-------------|------|-------------|-------------|
| **Stop Camera** | 🟠 Orange | - | End of daily class | ✅ After 12h |
| **End Session** | 🔴 Red | ⏹️ | Semester end | ❌ Never |
| **Reopen Session** | 🟢 Green | 🔄 | After 12 hours | - |

## Status Indicators

| Badge | Meaning | What You Can Do |
|-------|---------|-----------------|
| 🟢 Active | Session running | Stop Camera, End Session |
| 🟠 Stopped (Daily) | Waiting 12h | Reopen (if 12h passed), View Details |
| 🔴 Ended (Semester) | Permanent | View Details only |
| ⏳ Reopen in X.Xh | Countdown | Wait, View Details |

## Quick Actions

### Stop Camera (Daily)
```
1. Click "Stop Camera" button
2. Confirm action
3. Absent students marked automatically
4. Can reopen after 12 hours
```

### End Session (Permanent)
```
1. Click "End Session" button
2. Confirm permanent end
3. Cannot be reopened
4. Use only at semester end
```

### Reopen Session
```
1. Wait 12 hours after stopping
2. Click "🔄 Reopen Session" button
3. Confirm action
4. Session becomes active
5. Old records preserved
```

## Data Storage

```
All attendance records are PERMANENT
├── Day 1: 25 present, 5 absent
├── Day 2: 28 present, 2 absent
└── Day 3: 30 present, 0 absent

✅ No data is lost when reopening
✅ Reports show complete history
```

## Common Questions

**Q: Can I reopen immediately after stopping?**
A: No, must wait 12 hours.

**Q: Will old attendance be deleted?**
A: No, all records are permanent.

**Q: What's the difference between Stop Camera and End Session?**
A: Stop Camera = temporary (can reopen), End Session = permanent (cannot reopen).

**Q: How do I know when I can reopen?**
A: Dashboard shows countdown timer or "🔄 Reopen Session" button.

**Q: Can I reopen multiple times?**
A: Yes, unlimited reopens for stopped sessions.

## Testing (Quick)

```sql
-- Manually set session to 13 hours ago (for testing)
UPDATE sessions 
SET end_time = DATE_SUB(NOW(), INTERVAL 13 HOUR) 
WHERE id = <session_id>;

-- Then refresh dashboard to see reopen button
```

## Files to Read

- `TIME_BLOCK_SESSIONS_COMPLETE.md` - Full technical docs
- `STOP_CAMERA_VISUAL_GUIDE.md` - Visual guide with examples
- `test_session_management.py` - Test script

## Need Help?

1. Check status badge on dashboard
2. Look for countdown timer
3. Refresh page (Ctrl+F5)
4. Check backend logs
5. Verify 12 hours have passed

---

**Remember:** 
- 🟠 Stop Camera = Can reopen after 12h
- 🔴 End Session = Permanent, cannot reopen
- 🔄 Reopen = Preserves all old records
