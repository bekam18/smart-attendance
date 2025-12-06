import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING ACTUAL ATTENDANCE DATA")
print("="*60)

# Get all attendance records
sql = 'SELECT * FROM attendance ORDER BY date DESC, timestamp DESC LIMIT 20'
records = db.execute_query(sql)

print(f"\nFound {len(records)} recent attendance records:\n")

for i, record in enumerate(records, 1):
    print(f"{i}. student_id={record.get('student_id')}, "
          f"course='{record.get('course_name')}', "
          f"section={record.get('section_id')}, "
          f"session_id={record.get('session_id')}, "
          f"status={record.get('status')}, "
          f"date={record.get('date')}, "
          f"instructor_id={record.get('instructor_id')}")

# Get distinct courses
print("\n" + "="*60)
print("DISTINCT COURSES IN ATTENDANCE:")
print("="*60)
sql2 = 'SELECT DISTINCT course_name, COUNT(*) as count FROM attendance GROUP BY course_name'
courses = db.execute_query(sql2)
for course in courses:
    print(f"  - '{course['course_name']}': {course['count']} records")

# Get date range
print("\n" + "="*60)
print("DATE RANGE IN ATTENDANCE:")
print("="*60)
sql3 = 'SELECT MIN(date) as min_date, MAX(date) as max_date FROM attendance'
dates = db.execute_query(sql3)
print(f"  Min date: {dates[0]['min_date']}")
print(f"  Max date: {dates[0]['max_date']}")

print("\n" + "="*60)
