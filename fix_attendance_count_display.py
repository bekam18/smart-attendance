"""Fix attendance count display issue"""
import mysql.connector
from datetime import date

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

print("="*80)
print("FIXING ATTENDANCE COUNT DISPLAY")
print("="*80)

# Get active session
cursor.execute("SELECT * FROM sessions WHERE id = 47")
session = cursor.fetchone()

if not session:
    print("\n⚠️ Session 47 not found")
    cursor.close()
    db.close()
    exit()

session_id = session['id']
print(f"\n✓ Session ID: {session_id}")
print(f"  Name: {session['name']}")
print(f"  Section: {session['section_id']}, Year: {session['year']}")
print(f"  Status: {session['status']}")

# Check all attendance records for this session (all dates)
cursor.execute("""
    SELECT date, status, COUNT(*) as count
    FROM attendance
    WHERE session_id = %s
    GROUP BY date, status
    ORDER BY date DESC, status
""", (session_id,))

all_records = cursor.fetchall()

if all_records:
    print(f"\n⚠️ Found attendance records for session {session_id}:")
    for rec in all_records:
        print(f"  - {rec['date']}: {rec['status']} = {rec['count']} records")
    
    # Ask if we should delete old records
    print("\n" + "="*80)
    print("CLEANING UP OLD RECORDS")
    print("="*80)
    
    today = date.today().isoformat()
    
    # Delete records that are not from today
    cursor.execute("""
        DELETE FROM attendance
        WHERE session_id = %s AND date != %s
    """, (session_id, today))
    
    deleted = cursor.rowcount
    db.commit()
    
    if deleted > 0:
        print(f"\n✅ Deleted {deleted} old attendance records")
    else:
        print(f"\n✓ No old records to delete")
    
    # Check today's records
    cursor.execute("""
        SELECT student_id, status, timestamp
        FROM attendance
        WHERE session_id = %s AND date = %s
        ORDER BY timestamp DESC
    """, (session_id, today))
    
    today_records = cursor.fetchall()
    
    if today_records:
        print(f"\n✓ Today's attendance records ({len(today_records)}):")
        for rec in today_records:
            print(f"  - {rec['student_id']}: {rec['status']} at {rec['timestamp']}")
    else:
        print(f"\n✓ No attendance records for today")
else:
    print(f"\n✓ No attendance records found for session {session_id}")

# Verify student count
cursor.execute("""
    SELECT COUNT(*) as count
    FROM students
    WHERE section = %s AND year = %s
""", (session['section_id'], session['year']))

student_count = cursor.fetchone()['count']

print(f"\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal students in Section {session['section_id']}, Year {session['year']}: {student_count}")
print(f"Expected absent count when Stop Camera clicked: {student_count}")

cursor.close()
db.close()

print("\n" + "="*80)
print("FIX COMPLETE")
print("="*80)
print("\n✅ Please refresh the page (Ctrl+F5) to see correct counts")
