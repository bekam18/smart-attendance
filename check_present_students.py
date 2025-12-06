import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING PRESENT STUDENTS")
print("="*60)

# Get all present records
sql = '''
    SELECT student_id, course_name, section_id, session_id, status, date, instructor_id
    FROM attendance 
    WHERE status = 'present'
    ORDER BY course_name, student_id
'''
present_records = db.execute_query(sql)

print(f"\nTotal PRESENT records: {len(present_records)}\n")

for record in present_records:
    print(f"  ✅ {record['student_id']}")
    print(f"     Course: {record['course_name']}")
    print(f"     Section: {record['section_id']}")
    print(f"     Session: {record['session_id']}")
    print(f"     Date: {record['date']}")
    print(f"     Instructor: {record['instructor_id']}")
    print()

# Get all absent records for Mobile Development
print("="*60)
print("MOBILE DEVELOPMENT - ALL RECORDS:")
print("="*60)
sql2 = '''
    SELECT student_id, session_id, status
    FROM attendance 
    WHERE course_name = 'Mobile Development'
    ORDER BY session_id, student_id
'''
mobile_records = db.execute_query(sql2)

from collections import defaultdict
by_session = defaultdict(list)
for record in mobile_records:
    by_session[record['session_id']].append(record)

for session_id, records in sorted(by_session.items()):
    present = sum(1 for r in records if r['status'] == 'present')
    absent = sum(1 for r in records if r['status'] == 'absent')
    print(f"\nSession {session_id}: {present} present, {absent} absent")
    
    # Show present students
    present_students = [r['student_id'] for r in records if r['status'] == 'present']
    if present_students:
        print(f"  Present: {', '.join(present_students)}")
    
    # Show first few absent
    absent_students = [r['student_id'] for r in records if r['status'] == 'absent']
    if absent_students:
        print(f"  Absent: {', '.join(absent_students[:5])}{'...' if len(absent_students) > 5 else ''}")

print("\n" + "="*60)
