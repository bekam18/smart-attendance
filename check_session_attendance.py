"""Check attendance records for active session"""
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
print("CHECKING ATTENDANCE FOR ACTIVE SESSION")
print("="*80)

# Get active session
cursor.execute("SELECT * FROM sessions WHERE status = 'active' ORDER BY start_time DESC LIMIT 1")
session = cursor.fetchone()

if not session:
    print("\n⚠️ No active session found")
    cursor.close()
    db.close()
    exit()

session_id = session['id']
print(f"\n✓ Active Session ID: {session_id}")
print(f"  Name: {session['name']}")
print(f"  Section: {session['section_id']}, Year: {session['year']}")

# Get all attendance records for this session today
today = date.today().isoformat()

cursor.execute("""
    SELECT student_id, status, timestamp, confidence
    FROM attendance
    WHERE session_id = %s AND date = %s
    ORDER BY student_id, timestamp DESC
""", (session_id, today))

records = cursor.fetchall()

print(f"\n✓ Found {len(records)} attendance records for today:")

# Count by status
present_count = 0
absent_count = 0
student_records = {}

for record in records:
    student_id = record['student_id']
    status = record['status']
    
    if student_id not in student_records:
        student_records[student_id] = []
    student_records[student_id].append(record)
    
    if status == 'present':
        present_count += 1
    else:
        absent_count += 1

print(f"\n  Total records: {len(records)}")
print(f"  Present records: {present_count}")
print(f"  Absent records: {absent_count}")

# Check for duplicate records per student
print("\n" + "="*80)
print("CHECKING FOR DUPLICATE RECORDS PER STUDENT")
print("="*80)

duplicates_found = False
for student_id, student_recs in student_records.items():
    if len(student_recs) > 1:
        duplicates_found = True
        print(f"\n⚠️ {student_id} has {len(student_recs)} records:")
        for rec in student_recs:
            print(f"    - {rec['status']} at {rec['timestamp']} (confidence: {rec['confidence']})")

if not duplicates_found:
    print("\n✅ No duplicate records per student")

# Show unique students
print("\n" + "="*80)
print("UNIQUE STUDENTS IN ATTENDANCE")
print("="*80)

unique_present = set()
unique_absent = set()

for student_id, student_recs in student_records.items():
    # Get latest record for each student
    latest = student_recs[0]  # Already sorted by timestamp DESC
    if latest['status'] == 'present':
        unique_present.add(student_id)
    else:
        unique_absent.add(student_id)

print(f"\nUnique students:")
print(f"  Present: {len(unique_present)}")
print(f"  Absent: {len(unique_absent)}")
print(f"  Total: {len(unique_present) + len(unique_absent)}")

# List all students
if unique_present:
    print(f"\nPresent students ({len(unique_present)}):")
    for sid in sorted(unique_present):
        print(f"  - {sid}")

if unique_absent:
    print(f"\nAbsent students ({len(unique_absent)}):")
    for sid in sorted(unique_absent):
        print(f"  - {sid}")

# Check if there are records for students not in Section A, Year 4
print("\n" + "="*80)
print("CHECKING FOR INVALID STUDENT RECORDS")
print("="*80)

cursor.execute("""
    SELECT DISTINCT a.student_id
    FROM attendance a
    LEFT JOIN students s ON a.student_id = s.student_id
    WHERE a.session_id = %s AND a.date = %s
    AND (s.student_id IS NULL OR s.section != %s OR s.year != %s)
""", (session_id, today, session['section_id'], session['year']))

invalid_records = cursor.fetchall()

if invalid_records:
    print(f"\n❌ Found {len(invalid_records)} attendance records for students not in Section {session['section_id']}, Year {session['year']}:")
    for rec in invalid_records:
        print(f"  - {rec['student_id']}")
else:
    print(f"\n✅ All attendance records are for valid students in Section {session['section_id']}, Year {session['year']}")

cursor.close()
db.close()

print("\n" + "="*80)
print("CHECK COMPLETE")
print("="*80)
