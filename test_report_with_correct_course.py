import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("TESTING REPORT WITH CORRECT COURSE NAME")
print("="*60)

# Test parameters - using CORRECT course name
user_id = 58  # bacha instructor
section_id = 'A'
course_name = 'Mobile Development'  # ✅ CORRECT course name
start_date = '2025-12-01'  # ✅ CORRECT year (2025, not 2024)
end_date = '2025-12-31'

print(f"\nTest Parameters:")
print(f"  user_id: {user_id}")
print(f"  section_id: {section_id}")
print(f"  course_name: {course_name}")
print(f"  start_date: {start_date}")
print(f"  end_date: {end_date}")

# Build the query
sql = 'SELECT * FROM attendance WHERE 1=1'
params = []

sql += ' AND instructor_id = %s'
params.append(user_id)

if section_id:
    sql += ' AND section_id = %s'
    params.append(section_id)

if course_name:
    sql += ' AND course_name = %s'
    params.append(course_name)

if start_date:
    sql += ' AND date >= %s'
    params.append(start_date)

if end_date:
    sql += ' AND date <= %s'
    params.append(end_date)

sql += ' ORDER BY date, timestamp'

print(f"\nQuery:")
print(f"  SQL: {sql}")
print(f"  Params: {params}")

# Execute the query
records = db.execute_query(sql, tuple(params))
print(f"\n✅ Query Results: {len(records)} records found")

if records:
    print(f"\nFirst 5 records:")
    for i, record in enumerate(records[:5]):
        print(f"  [{i+1}] student_id={record.get('student_id')}, "
              f"session_id={record.get('session_id')}, "
              f"status={record.get('status')}, "
              f"date={record.get('date')}")
    
    # Calculate statistics
    session_ids = set()
    student_stats = {}
    
    for record in records:
        session_id = record.get('session_id')
        if session_id:
            session_ids.add(session_id)
        
        student_id = record['student_id']
        if student_id not in student_stats:
            student_stats[student_id] = {
                'present': 0,
                'absent': 0
            }
        
        if record.get('status') == 'present':
            student_stats[student_id]['present'] += 1
        elif record.get('status') == 'absent':
            student_stats[student_id]['absent'] += 1
    
    print(f"\n📊 Statistics:")
    print(f"  Total unique sessions: {len(session_ids)}")
    print(f"  Session IDs: {sorted(session_ids)}")
    print(f"  Total unique students: {len(student_stats)}")
    
    print(f"\n  Student breakdown:")
    for student_id, stats in sorted(student_stats.items()):
        print(f"    {student_id}: {stats['present']} present, {stats['absent']} absent")

# Get students in section
student_sql = 'SELECT student_id, name FROM students WHERE section = %s'
students = db.execute_query(student_sql, (section_id,))
print(f"\n👥 Students in section {section_id}: {len(students)}")
for student in students[:5]:
    print(f"  - {student['student_id']}: {student['name']}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
if len(records) > 0:
    print("✅ Report should work with these parameters!")
    print(f"   - Use course: 'Mobile Development' (not 'Web')")
    print(f"   - Use date range: 2025-12-01 to 2025-12-31 (not 2024)")
else:
    print("❌ Still no records found")
print("="*60)
