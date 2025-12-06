import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING INSTRUCTOR BEKI'S COURSES")
print("="*60)

# Get beki's info
sql = 'SELECT id, username, name, courses FROM users WHERE username = "beki"'
user = db.execute_query(sql)[0]

print(f"\nInstructor: {user['name']} (ID: {user['id']})")
print(f"Courses in profile: {user['courses']}")

# Check which courses have actual attendance data
print(f"\n" + "="*60)
print("COURSES WITH ATTENDANCE DATA:")
print("="*60)

sql2 = '''
    SELECT course_name, COUNT(*) as total_records,
           SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
           SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent_count
    FROM attendance
    WHERE instructor_id = %s
    GROUP BY course_name
'''
courses = db.execute_query(sql2, (user['id'],))

if courses:
    for course in courses:
        print(f"\n✅ {course['course_name']}")
        print(f"   Total records: {course['total_records']}")
        print(f"   Present: {course['present_count']}")
        print(f"   Absent: {course['absent_count']}")
else:
    print("\n❌ NO ATTENDANCE DATA FOR THIS INSTRUCTOR!")

# Check all courses in attendance table
print(f"\n" + "="*60)
print("ALL COURSES IN ATTENDANCE TABLE:")
print("="*60)

sql3 = '''
    SELECT DISTINCT course_name, instructor_id
    FROM attendance
    ORDER BY course_name
'''
all_courses = db.execute_query(sql3)

for course in all_courses:
    print(f"  - '{course['course_name']}' (instructor_id: {course['instructor_id']})")

print("\n" + "="*60)
print("SOLUTION:")
print("="*60)
print("\nIn the UI, you MUST select:")
if courses:
    print(f"  Course: '{courses[0]['course_name']}'")
else:
    print("  ⚠️  No courses available for this instructor")
print("  Section: A")
print("  Date: 2025-12-06")
print("\n" + "="*60)
