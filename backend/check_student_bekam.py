from db.mysql import get_db

db = get_db()

# Check Bekam Ayele's info
student = db.execute_query('SELECT student_id, name, section, year FROM students WHERE student_id = "STU013"')
if student:
    print(f"Student: {student[0]['name']}")
    print(f"Section: {student[0]['section']}")
    print(f"Year: {student[0]['year']}")
else:
    print("Student not found")

# Check instructor's year
instructor = db.execute_query('SELECT id, name, class_year FROM users WHERE name = "bekam"')
if instructor:
    print(f"\nInstructor: {instructor[0]['name']}")
    print(f"Class Year: {instructor[0]['class_year']}")
else:
    print("\nInstructor not found")

# Check latest session
session = db.execute_query('SELECT id, name, section_id, year FROM sessions ORDER BY start_time DESC LIMIT 1')
if session:
    print(f"\nLatest Session: {session[0]['name']}")
    print(f"Section: {session[0]['section_id']}")
    print(f"Year: {session[0]['year']}")
