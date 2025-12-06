import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("DIAGNOSING REPORT GENERATION QUERY")
print("="*60)

# Test parameters
user_id = 58  # bacha instructor
section_id = 'A'
course_name = 'Web'
start_date = '2024-12-01'
end_date = '2024-12-31'

print(f"\nTest Parameters:")
print(f"  user_id: {user_id}")
print(f"  section_id: {section_id}")
print(f"  course_name: {course_name}")
print(f"  start_date: {start_date}")
print(f"  end_date: {end_date}")

# Build the exact query from the endpoint
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

print(f"\n1. Full Query:")
print(f"   SQL: {sql}")
print(f"   Params: {params}")

# Execute the query
records = db.execute_query(sql, tuple(params))
print(f"\n2. Query Results: {len(records)} records found")

if records:
    print(f"\n   First 3 records:")
    for i, record in enumerate(records[:3]):
        print(f"   [{i+1}] student_id={record.get('student_id')}, "
              f"session_id={record.get('session_id')}, "
              f"status={record.get('status')}, "
              f"date={record.get('date')}")
else:
    print("\n   ❌ NO RECORDS FOUND!")
    
    # Try without filters one by one
    print("\n3. Testing filters individually:")
    
    # Just instructor_id
    sql1 = 'SELECT COUNT(*) as count FROM attendance WHERE instructor_id = %s'
    result1 = db.execute_query(sql1, (user_id,))
    print(f"   - instructor_id={user_id}: {result1[0]['count']} records")
    
    # instructor_id + section_id
    sql2 = 'SELECT COUNT(*) as count FROM attendance WHERE instructor_id = %s AND section_id = %s'
    result2 = db.execute_query(sql2, (user_id, section_id))
    print(f"   - instructor_id={user_id} + section_id={section_id}: {result2[0]['count']} records")
    
    # instructor_id + course_name
    sql3 = 'SELECT COUNT(*) as count FROM attendance WHERE instructor_id = %s AND course_name = %s'
    result3 = db.execute_query(sql3, (user_id, course_name))
    print(f"   - instructor_id={user_id} + course_name={course_name}: {result3[0]['count']} records")
    
    # Check what course_names exist
    sql4 = 'SELECT DISTINCT course_name FROM attendance WHERE instructor_id = %s'
    result4 = db.execute_query(sql4, (user_id,))
    print(f"   - Available course_names for instructor {user_id}:")
    for row in result4:
        print(f"     * '{row['course_name']}'")
    
    # Check what section_ids exist
    sql5 = 'SELECT DISTINCT section_id FROM attendance WHERE instructor_id = %s'
    result5 = db.execute_query(sql5, (user_id,))
    print(f"   - Available section_ids for instructor {user_id}:")
    for row in result5:
        print(f"     * '{row['section_id']}'")

# Check students query
print(f"\n4. Students Query:")
student_sql = 'SELECT * FROM students WHERE section = %s'
students = db.execute_query(student_sql, (section_id,))
print(f"   Found {len(students)} students in section {section_id}")

# Check unique sessions
print(f"\n5. Unique Sessions:")
session_sql = '''
    SELECT DISTINCT session_id, session_type, date 
    FROM attendance 
    WHERE instructor_id = %s AND section_id = %s
    ORDER BY date
'''
sessions = db.execute_query(session_sql, (user_id, section_id))
print(f"   Found {len(sessions)} unique sessions")
for session in sessions:
    print(f"   - session_id={session['session_id']}, type={session['session_type']}, date={session['date']}")

print("\n" + "="*60)
