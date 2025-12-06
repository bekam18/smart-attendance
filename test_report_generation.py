import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("TESTING REPORT GENERATION DATA")
print("="*60 + "\n")

# Test parameters
section_id = 'A'
course_name = 'Web'
start_date = '2025-12-01'
end_date = '2025-12-31'

print(f"Test Parameters:")
print(f"  Section: {section_id}")
print(f"  Course: {course_name}")
print(f"  Date Range: {start_date} to {end_date}\n")

# Check attendance records
print("1. Checking attendance records:")
sql = """
    SELECT * FROM attendance 
    WHERE section_id = %s 
    AND course_name = %s 
    AND date >= %s 
    AND date <= %s
    ORDER BY date, timestamp
"""
records = db.execute_query(sql, (section_id, course_name, start_date, end_date))
print(f"   Found {len(records)} attendance records\n")

if records:
    print("   Sample records:")
    for i, record in enumerate(records[:5]):
        print(f"   {i+1}. Student: {record['student_id']}, Session: {record.get('session_id')}, Status: {record.get('status')}, Type: {record.get('session_type')}")
    
    # Check unique sessions
    session_ids = set()
    for record in records:
        if record.get('session_id'):
            session_ids.add(record['session_id'])
    
    print(f"\n   Unique session IDs: {session_ids}")
    print(f"   Total unique sessions: {len(session_ids)}")
else:
    print("   ❌ No attendance records found!")
    print("\n   Checking without date filter:")
    sql = "SELECT * FROM attendance WHERE section_id = %s AND course_name = %s LIMIT 5"
    records = db.execute_query(sql, (section_id, course_name))
    print(f"   Found {len(records)} records without date filter")
    if records:
        print("   Sample:")
        for record in records[:3]:
            print(f"     Date: {record['date']}, Student: {record['student_id']}, Status: {record.get('status')}")

# Check students
print("\n2. Checking students in section:")
sql = "SELECT * FROM students WHERE section = %s"
students = db.execute_query(sql, (section_id,))
print(f"   Found {len(students)} students in section {section_id}")
if students:
    print("   Sample students:")
    for student in students[:5]:
        print(f"     {student['student_id']}: {student['name']}")

# Check sessions
print("\n3. Checking sessions:")
sql = "SELECT * FROM sessions WHERE section_id = %s AND course_name = %s"
sessions = db.execute_query(sql, (section_id, course_name))
print(f"   Found {len(sessions)} sessions")
if sessions:
    print("   Sessions:")
    for session in sessions:
        print(f"     ID: {session['id']}, Type: {session.get('session_type')}, Status: {session.get('status')}")

print("\n" + "="*60 + "\n")
