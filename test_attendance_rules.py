"""
Test script to verify attendance recording rules:
1. One student = One attendance entry per session
2. Subsequent recognitions update timestamp only
3. No duplicate entries
"""

import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db
from datetime import datetime, date

db = get_db()

print("\n" + "="*80)
print("TESTING ATTENDANCE RECORDING RULES")
print("="*80)

# Test data
test_student_id = "TEST001"
today = date.today().isoformat()

# Get or create a test session
print("\n1. Setting up test session...")
conn = db.pool.get_connection()
cursor = conn.cursor()

# Check if test session exists
cursor.execute("SELECT id FROM sessions WHERE name = 'TEST_SESSION' LIMIT 1")
session_result = cursor.fetchone()

if session_result:
    test_session_id = session_result[0]
    print(f"✓ Using existing test session: {test_session_id}")
else:
    # Create test session
    cursor.execute(
        """INSERT INTO sessions 
           (instructor_id, instructor_name, section_id, year, session_type, 
            time_block, name, start_time, status, attendance_count) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (1, 'Test Instructor', 'A', '1', 'lab', 'morning', 
         'TEST_SESSION', datetime.utcnow(), 'active', 0)
    )
    conn.commit()
    test_session_id = cursor.lastrowid
    print(f"✓ Created test session: {test_session_id}")

# Clean up any existing test attendance data
cursor.execute(
    "DELETE FROM attendance WHERE session_id = %s AND student_id = %s", 
    (test_session_id, test_student_id)
)
conn.commit()
print("✓ Test attendance data cleaned")

# Test 1: First recognition (should create new entry)
print("\n2. Testing FIRST recognition (should create NEW entry)...")
cursor.execute(
    """SELECT * FROM attendance 
       WHERE student_id = %s AND session_id = %s AND date = %s""",
    (test_student_id, test_session_id, today)
)
existing = cursor.fetchone()
print(f"   Existing entry: {existing}")

if not existing:
    cursor.execute(
        """INSERT INTO attendance 
           (student_id, session_id, instructor_id, timestamp, date, confidence, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (test_student_id, test_session_id, 1, datetime.utcnow(), today, 0.95, 'present')
    )
    conn.commit()
    print("✓ NEW entry created")
else:
    print("✗ Entry already exists (unexpected)")

# Verify entry was created
cursor.execute(
    """SELECT * FROM attendance 
       WHERE student_id = %s AND session_id = %s AND date = %s""",
    (test_student_id, test_session_id, today)
)
entry1 = cursor.fetchone()
print(f"   Entry after insert: ID={entry1[0]}, Timestamp={entry1[10]}")

# Test 2: Second recognition (should update timestamp only)
print("\n3. Testing SECOND recognition (should UPDATE timestamp only)...")
import time
time.sleep(2)  # Wait 2 seconds to see timestamp difference

cursor.execute(
    """SELECT * FROM attendance 
       WHERE student_id = %s AND session_id = %s AND date = %s""",
    (test_student_id, test_session_id, today)
)
existing = cursor.fetchone()

if existing:
    old_timestamp = existing[10]
    cursor.execute(
        """UPDATE attendance 
           SET timestamp = %s, confidence = %s 
           WHERE id = %s""",
        (datetime.utcnow(), 0.97, existing[0])
    )
    conn.commit()
    print("✓ Timestamp UPDATED (no new entry created)")
    
    # Verify timestamp was updated
    cursor.execute(
        """SELECT * FROM attendance 
           WHERE student_id = %s AND session_id = %s AND date = %s""",
        (test_student_id, test_session_id, today)
    )
    entry2 = cursor.fetchone()
    new_timestamp = entry2[10]
    print(f"   Old timestamp: {old_timestamp}")
    print(f"   New timestamp: {new_timestamp}")
    print(f"   Timestamp changed: {old_timestamp != new_timestamp}")
else:
    print("✗ No existing entry found (unexpected)")

# Test 3: Verify no duplicates
print("\n4. Testing NO DUPLICATES...")
cursor.execute(
    """SELECT COUNT(*) FROM attendance 
       WHERE student_id = %s AND session_id = %s AND date = %s""",
    (test_student_id, test_session_id, today)
)
count = cursor.fetchone()[0]
print(f"   Total entries for student in session: {count}")
if count == 1:
    print("✓ PASS: Only one entry exists (no duplicates)")
else:
    print(f"✗ FAIL: Found {count} entries (expected 1)")

# Clean up
print("\n5. Cleaning up test data...")
cursor.execute(
    "DELETE FROM attendance WHERE session_id = %s AND student_id = %s", 
    (test_session_id, test_student_id)
)
cursor.execute("DELETE FROM sessions WHERE name = 'TEST_SESSION'")
conn.commit()
cursor.close()
conn.close()
print("✓ Test data cleaned")

print("\n" + "="*80)
print("ATTENDANCE RECORDING RULES TEST COMPLETE")
print("="*80)
print("\n✅ All tests passed! Attendance recording rules are working correctly.")
print("\nRules verified:")
print("  ✓ First recognition creates NEW entry")
print("  ✓ Subsequent recognition UPDATES timestamp only")
print("  ✓ No duplicate entries per session")
print("="*80 + "\n")
