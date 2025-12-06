import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING INSTRUCTOR COURSES")
print("="*60)

# Get instructor info
sql = 'SELECT id, username, name, courses FROM users WHERE role = "instructor"'
instructors = db.execute_query(sql)

print(f"\nFound {len(instructors)} instructors:\n")

for instructor in instructors:
    print(f"ID: {instructor['id']}")
    print(f"Username: {instructor['username']}")
    print(f"Name: {instructor['name']}")
    print(f"Courses: {instructor.get('courses')}")
    print()

# Check what courses exist in sessions
print("="*60)
print("COURSES IN SESSIONS TABLE:")
print("="*60)
sql2 = 'SELECT DISTINCT course_name FROM sessions'
courses = db.execute_query(sql2)
print("\nCourses in sessions:")
for course in courses:
    print(f"  - '{course['course_name']}'")

# Check what courses exist in attendance
print("\n" + "="*60)
print("COURSES IN ATTENDANCE TABLE:")
print("="*60)
sql3 = 'SELECT DISTINCT course_name FROM attendance'
courses = db.execute_query(sql3)
print("\nCourses in attendance:")
for course in courses:
    print(f"  - '{course['course_name']}'")

print("\n" + "="*60)
