"""
Check all data in the database
"""

import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("DATABASE OVERVIEW")
print("=" * 60)

# Check students
cursor.execute("SELECT COUNT(*) as count FROM students")
student_count = cursor.fetchone()['count']
print(f"\nTotal Students: {student_count}")

if student_count > 0:
    cursor.execute("SELECT student_id, name, year, section FROM students LIMIT 5")
    students = cursor.fetchall()
    print("\nSample Students:")
    for s in students:
        print(f"  - {s['student_id']}: {s['name']} (Year: {s['year']}, Section: {s['section']})")

# Check instructors
cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'instructor'")
instructor_count = cursor.fetchone()['count']
print(f"\nTotal Instructors: {instructor_count}")

if instructor_count > 0:
    cursor.execute("SELECT id, name, course_name, class_year, sections FROM users WHERE role = 'instructor' LIMIT 5")
    instructors = cursor.fetchall()
    print("\nSample Instructors:")
    for i in instructors:
        print(f"  - {i['name']}: {i['course_name']} (Year: {i['class_year']}, Sections: {i['sections']})")

# Check attendance
cursor.execute("SELECT COUNT(*) as count FROM attendance")
attendance_count = cursor.fetchone()['count']
print(f"\nTotal Attendance Records: {attendance_count}")

if attendance_count > 0:
    cursor.execute("SELECT DISTINCT course_name FROM attendance WHERE course_name IS NOT NULL")
    courses = cursor.fetchall()
    print(f"\nCourses in Attendance Records: {len(courses)}")
    for c in courses:
        print(f"  - {c['course_name']}")
    
    cursor.execute("SELECT student_id, course_name, COUNT(*) as count FROM attendance GROUP BY student_id, course_name LIMIT 5")
    records = cursor.fetchall()
    print("\nSample Attendance by Student and Course:")
    for r in records:
        print(f"  - {r['student_id']}: {r['course_name']} ({r['count']} records)")

# Check sessions
cursor.execute("SELECT COUNT(*) as count FROM sessions")
session_count = cursor.fetchone()['count']
print(f"\nTotal Sessions: {session_count}")

if session_count > 0:
    cursor.execute("SELECT name, course_name, year, section_id, session_type FROM sessions LIMIT 5")
    sessions = cursor.fetchall()
    print("\nSample Sessions:")
    for s in sessions:
        print(f"  - {s['name']}: {s['course_name']} (Year: {s['year']}, Section: {s['section_id']}, Type: {s['session_type']})")

cursor.close()
conn.close()

print("\n" + "=" * 60)
