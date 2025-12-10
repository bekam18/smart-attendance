"""Test the duplicate prevention logic"""
import mysql.connector
from datetime import datetime, timedelta, date

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

print("="*80)
print("TESTING DUPLICATE PREVENTION LOGIC")
print("="*80)

# Get STU013's recent attendance
student_id = 'STU013'
session_id = 47
today = date.today().isoformat()

print(f"\nChecking recent attendance for {student_id}:")
print(f"  Session ID: {session_id}")
print(f"  Date: {today}")

# Get all records for this student today
cursor.execute("""
    SELECT id, student_id, timestamp, confidence, status
    FROM attendance
    WHERE student_id = %s AND session_id = %s AND date = %s
    ORDER BY timestamp DESC
""", (student_id, session_id, today))

records = cursor.fetchall()

print(f"\n✓ Found {len(records)} records:")
for rec in records:
    print(f"  - ID {rec['id']}: {rec['status']} at {rec['timestamp']} (confidence: {rec['confidence']})")

# Test the 5-minute check
print("\n" + "="*80)
print("TESTING 5-MINUTE CHECK")
print("="*80)

five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
print(f"\nCurrent UTC time: {datetime.utcnow()}")
print(f"5 minutes ago: {five_minutes_ago}")

cursor.execute("""
    SELECT * FROM attendance 
    WHERE student_id = %s 
    AND session_id = %s 
    AND date = %s 
    AND timestamp > %s
    ORDER BY timestamp DESC
    LIMIT 1
""", (student_id, session_id, today, five_minutes_ago))

recent = cursor.fetchone()

if recent:
    print(f"\n✓ Found recent record within 5 minutes:")
    print(f"  ID: {recent['id']}")
    print(f"  Timestamp: {recent['timestamp']}")
    print(f"  Time difference: {datetime.utcnow() - recent['timestamp']}")
    print(f"\n  → Should UPDATE this record, not create new one")
else:
    print(f"\n✓ No record found within last 5 minutes")
    print(f"  → Should CREATE new record")

# Check if there are duplicates within 5 minutes
print("\n" + "="*80)
print("CHECKING FOR DUPLICATES WITHIN 5 MINUTES")
print("="*80)

if len(records) >= 2:
    for i in range(len(records) - 1):
        rec1 = records[i]
        rec2 = records[i + 1]
        time_diff = rec1['timestamp'] - rec2['timestamp']
        seconds = time_diff.total_seconds()
        
        if seconds < 300:  # 5 minutes = 300 seconds
            print(f"\n❌ DUPLICATE FOUND:")
            print(f"  Record 1: ID {rec1['id']} at {rec1['timestamp']}")
            print(f"  Record 2: ID {rec2['id']} at {rec2['timestamp']}")
            print(f"  Time difference: {seconds:.1f} seconds")
            print(f"  → This should have been prevented!")

# Check timestamp column type
print("\n" + "="*80)
print("CHECKING TIMESTAMP COLUMN TYPE")
print("="*80)

cursor.execute("""
    SELECT COLUMN_TYPE, COLUMN_DEFAULT
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'smart_attendance'
    AND TABLE_NAME = 'attendance'
    AND COLUMN_NAME = 'timestamp'
""")

col_info = cursor.fetchone()
print(f"\nTimestamp column:")
print(f"  Type: {col_info['COLUMN_TYPE']}")
print(f"  Default: {col_info['COLUMN_DEFAULT']}")

cursor.close()
db.close()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
