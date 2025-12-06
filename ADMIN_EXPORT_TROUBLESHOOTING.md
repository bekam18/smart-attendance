# 🔧 Admin Export Troubleshooting Guide

## Issue: "Failed to export CSV"

### Updated Fix (v2)

The export functions have been improved with:
- ✅ Better error handling
- ✅ Detailed logging
- ✅ Safer record iteration
- ✅ Empty result handling
- ✅ Better CORS headers

### Steps to Fix

#### 1. Restart Backend
```bash
# Stop current backend (Ctrl+C)
cd backend
python app.py
```

#### 2. Check Backend Console

When you click export, you should see:
```
📊 CSV Export requested - Filters: course=None, section=None, year=None, date=None
📊 Found X records to export
✅ CSV generated successfully (XXX bytes)
```

If you see errors, they will be detailed in the console.

#### 3. Common Issues & Solutions

### Issue: "No records found"
**Symptom:** Export works but file is empty or only has headers

**Solution:**
1. Check if attendance records exist:
   ```sql
   SELECT COUNT(*) FROM attendance;
   ```
2. Try exporting without filters first
3. Check if filters are too restrictive

### Issue: "Database connection error"
**Symptom:** Error about MySQL connection or unread results

**Solution:**
1. Restart MySQL service
2. Check `.env` database credentials
3. Verify database exists:
   ```bash
   mysql -u root -p
   USE smart_attendance;
   SHOW TABLES;
   ```

### Issue: "Column not found"
**Symptom:** Error about missing column in query

**Solution:**
1. Check attendance table schema:
   ```sql
   DESCRIBE attendance;
   ```
2. Verify all columns exist:
   - id
   - student_id
   - course_name
   - section
   - year
   - session_id
   - status
   - confidence
   - timestamp
   - marked_by

### Issue: "CORS error persists"
**Symptom:** Still getting CORS error after restart

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+F5)
3. Check backend console for actual error
4. Verify CORS configuration in `app.py`

### Issue: "Excel export fails but CSV works"
**Symptom:** CSV downloads fine, Excel fails

**Solution:**
1. Check if pandas is installed:
   ```bash
   pip install pandas openpyxl
   ```
2. Check backend console for pandas errors
3. Try CSV export first to verify data

## Debugging Steps

### 1. Check Backend Logs

Look for these messages in backend console:
```
📊 CSV Export requested - Filters: ...
📊 Found X records to export
✅ CSV generated successfully
```

Or error messages:
```
❌ Error exporting CSV: ...
```

### 2. Test with curl

```bash
# Get your JWT token first (login as admin)
curl -X GET "http://localhost:5000/api/admin/attendance/export/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v

# Check response headers and status code
```

### 3. Check Database

```bash
# Connect to MySQL
mysql -u root -p

# Use database
USE smart_attendance;

# Check attendance records
SELECT COUNT(*) FROM attendance;

# Check sample record
SELECT * FROM attendance LIMIT 1;

# Check students table
SELECT COUNT(*) FROM students;
```

### 4. Verify Permissions

Make sure you're logged in as admin:
```bash
# Check user role in database
SELECT id, username, role FROM users WHERE role = 'admin';
```

## What Changed in v2

### Improved Error Handling
- Uses `.get()` method for safer dictionary access
- Handles None values gracefully
- Continues on row errors instead of failing completely

### Better Logging
- Shows filter parameters
- Shows record count
- Shows file size
- Shows detailed errors

### Enhanced Headers
- Added `charset=utf-8` for CSV
- Added `Cache-Control: no-cache`
- Better content disposition

### Empty Result Handling
- CSV: Returns file with headers only
- Excel: Returns empty DataFrame with headers

## Testing Checklist

- [ ] Backend restarts without errors
- [ ] Can access admin dashboard
- [ ] Backend console shows export request
- [ ] Backend console shows record count
- [ ] Backend console shows success message
- [ ] File downloads in browser
- [ ] File opens correctly
- [ ] Data is correct

## Still Not Working?

### Check These:

1. **Backend Console Output**
   - What error message appears?
   - Does it show the export request?
   - Does it show record count?

2. **Browser Console**
   - Any JavaScript errors?
   - What's the actual HTTP status code?
   - Check Network tab for response

3. **Database**
   - Are there attendance records?
   - Do students exist?
   - Are tables properly joined?

4. **Authentication**
   - Are you logged in as admin?
   - Is JWT token valid?
   - Check token expiration

### Get Detailed Error

Add this to see full error:
```python
# In backend console, you'll see:
❌ Error exporting CSV: [detailed error message]
[Full stack trace]
```

## Quick Test Script

```bash
# Run this to test export
test_admin_export.bat
```

Or manually:
```bash
# 1. Login and get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# 2. Copy the access_token from response

# 3. Test export
curl -X GET "http://localhost:5000/api/admin/attendance/export/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output test.csv

# 4. Check file
type test.csv
```

## Contact Info

If still having issues:
1. Check backend console for exact error
2. Check browser console for HTTP status
3. Verify database has records
4. Try CSV first, then Excel
5. Test with curl to isolate frontend issues

---

**Most common fix:** Just restart the backend! 🔄
