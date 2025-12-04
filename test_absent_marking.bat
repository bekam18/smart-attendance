@echo off
echo ============================================================
echo Testing Automatic Absent Marking Feature
echo ============================================================
echo.

echo This test verifies that students from the section are marked as absent
echo when the "Stop Camera" button is clicked.
echo.

echo Test Steps:
echo 1. Start a session for a specific section and year
echo 2. Mark some students as present (via camera recognition)
echo 3. Click "Stop Camera" button
echo 4. Verify remaining students from that section are marked absent
echo.

echo ============================================================
echo Checking Database for Students by Section
echo ============================================================
echo.

python -c "from backend.db.mysql import get_db; db = get_db(); sections = db.execute_query('SELECT DISTINCT section, year FROM students ORDER BY section, year'); print('\nStudents by Section/Year:'); [print(f\"  Section {s['section']}, Year {s['year']}: {db.execute_query('SELECT COUNT(*) as count FROM students WHERE section = %%s AND year = %%s', (s['section'], s['year']))[0]['count']} students\") for s in sections]"

echo.
echo ============================================================
echo Test Instructions:
echo ============================================================
echo.
echo 1. Login as instructor
echo 2. Start a session for a specific section (e.g., Section A, 4th Year)
echo 3. Let 2-3 students get recognized by camera
echo 4. Click "Stop Camera" button
echo 5. Check that remaining students from Section A, 4th Year are marked absent
echo 6. Verify students from OTHER sections are NOT marked absent
echo.

echo ============================================================
echo Expected Behavior:
echo ============================================================
echo.
echo If Section A, 4th Year has 10 students:
echo   - 3 students recognized = 3 PRESENT
echo   - Click "Stop Camera"
echo   - 7 remaining students = 7 ABSENT
echo   - Total: 10 students (all from Section A, 4th Year)
echo.
echo Students from Section B, C, D should NOT be affected!
echo.

echo ============================================================
echo Checking Recent Sessions
echo ============================================================
echo.

python -c "from backend.db.mysql import get_db; db = get_db(); sessions = db.execute_query('SELECT id, name, section_id, year, status, attendance_count, start_time FROM sessions ORDER BY start_time DESC LIMIT 5'); print('\nRecent Sessions:'); [print(f\"  ID: {s['id']} | {s['name']} | Section {s['section_id']}, Year {s['year']} | Status: {s['status']} | Count: {s['attendance_count']}\") for s in sessions]"

echo.
echo ============================================================
echo Test Complete
echo ============================================================
echo.
echo To verify the feature is working correctly:
echo 1. Check the attendance records for your session
echo 2. Confirm only students from the session's section/year are marked
echo 3. Verify present students have green badges
echo 4. Verify absent students have red badges
echo.

pause
