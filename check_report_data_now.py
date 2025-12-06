import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING CURRENT REPORT DATA")
print("="*60)

# Check what attendance records exist
print("\n1. ALL ATTENDANCE RECORDS:")
sql = '''
    SELECT student_id, course_name, section_id, session_id, status, date
    FROM attendance 
    ORDER BY date DESC, student_id
'''
records = db.execute_query(sql)
print(f"   Total records: {len(records)}\n")

# Group by course
from collections import defaultdict
by_course = defaultdict(list)
for record in records:
    by_course[record['course_name']].append(record)

for course, course_records in by_course.items():
    print(f"\n   Course: '{course}' ({len(course_records)} records)")
    
    # Count present/absent
    present = sum(1 for r in course_records if r['status'] == 'present')
    absent = sum(1 for r in course_records if r['status'] == 'absent')
    
    print(f"     Present: {present}, Absent: {absent}")
    
    # Show first few records
    print(f"     Sample records:")
    for r in course_records[:3]:
        print(f"       - {r['student_id']}: {r['status']} (session {r['session_id']}, date {r['date']})")

# Check instructor courses
print("\n" + "="*60)
print("2. INSTRUCTOR COURSES:")
print("="*60)
sql2 = 'SELECT id, username, name, courses FROM users WHERE role = "instructor"'
instructors = db.execute_query(sql2)

for inst in instructors:
    print(f"\n   {inst['name']} (ID: {inst['id']}, username: {inst['username']})")
    print(f"   Courses in profile: {inst['courses']}")
    
    # Check which courses have actual data
    sql3 = 'SELECT DISTINCT course_name FROM attendance WHERE instructor_id = %s'
    actual_courses = db.execute_query(sql3, (inst['id'],))
    print(f"   Courses with attendance data: {[c['course_name'] for c in actual_courses]}")

# Check sections
print("\n" + "="*60)
print("3. SECTIONS WITH DATA:")
print("="*60)
sql4 = '''
    SELECT DISTINCT course_name, section_id, COUNT(*) as count
    FROM attendance
    GROUP BY course_name, section_id
    ORDER BY course_name, section_id
'''
sections = db.execute_query(sql4)
for section in sections:
    print(f"   {section['course_name']} - Section {section['section_id']}: {section['count']} records")

# Check date range
print("\n" + "="*60)
print("4. DATE RANGE:")
print("="*60)
sql5 = 'SELECT MIN(date) as min_date, MAX(date) as max_date FROM attendance'
dates = db.execute_query(sql5)
print(f"   Earliest: {dates[0]['min_date']}")
print(f"   Latest: {dates[0]['max_date']}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("\nTo generate a working report, use:")
print("  - Course: 'Mobile Development' or 'OS'")
print("  - Section: 'A'")
print("  - Date range: 2025-12-01 to 2025-12-31")
print("\nDO NOT USE:")
print("  ❌ Course: 'Web' or 'Java' (no data)")
print("  ❌ Date range: 2024 (no data)")
print("="*60 + "\n")
