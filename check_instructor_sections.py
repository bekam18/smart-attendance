import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING INSTRUCTOR SECTIONS")
print("="*60 + "\n")

# Check instructor's sections field
print("1. Checking instructor's sections field:")
result = db.execute_query("SELECT id, username, name, sections FROM users WHERE role = 'instructor'")
for instructor in result:
    print(f"\nInstructor: {instructor['name']} ({instructor['username']})")
    print(f"  Sections field: {instructor.get('sections')}")

# Check actual sections in sessions table
print("\n2. Checking sections in sessions table:")
result = db.execute_query("SELECT DISTINCT section_id, course_name FROM sessions ORDER BY course_name, section_id")
print("\nSections by course:")
current_course = None
for row in result:
    if row['course_name'] != current_course:
        current_course = row['course_name']
        print(f"\n{current_course}:")
    print(f"  - Section {row['section_id']}")

# Check sections in students table
print("\n3. Checking sections in students table:")
result = db.execute_query("SELECT DISTINCT section FROM students WHERE section IS NOT NULL ORDER BY section")
print("\nStudent sections:")
for row in result:
    print(f"  - Section {row['section']}")

# Check sections in attendance table
print("\n4. Checking sections in attendance table:")
result = db.execute_query("SELECT DISTINCT section_id, course_name FROM attendance WHERE section_id IS NOT NULL ORDER BY course_name, section_id")
print("\nAttendance sections by course:")
current_course = None
for row in result:
    if row['course_name'] != current_course:
        current_course = row['course_name']
        print(f"\n{current_course}:")
    print(f"  - Section {row['section_id']}")

print("\n" + "="*60 + "\n")
