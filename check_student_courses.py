"""
Check student courses and instructors
"""

import mysql.connector
import json

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("CHECKING STUDENT COURSES")
print("=" * 60)

# Get a sample student
cursor.execute("SELECT * FROM students LIMIT 1")
student = cursor.fetchone()

if student:
    print(f"\nStudent: {student['name']} ({student['student_id']})")
    print(f"Year: {student['year']}, Section: {student['section']}")
    
    # Get courses from attendance
    cursor.execute("""
        SELECT DISTINCT course_name 
        FROM attendance 
        WHERE student_id = %s AND course_name IS NOT NULL AND course_name != ''
        ORDER BY course_name
    """, (student['student_id'],))
    
    courses_from_attendance = cursor.fetchall()
    print(f"\nCourses from attendance records: {len(courses_from_attendance)}")
    for course in courses_from_attendance:
        print(f"  - {course['course_name']}")
    
    # Get instructors for this student's year and section
    cursor.execute("""
        SELECT id, name, course_name, sections, class_year 
        FROM users 
        WHERE role = 'instructor' AND class_year = %s
    """, (student['year'],))
    
    instructors = cursor.fetchall()
    print(f"\nInstructors for year {student['year']}: {len(instructors)}")
    
    matching_instructors = []
    for instructor in instructors:
        sections_json = instructor.get('sections', '[]')
        try:
            sections = json.loads(sections_json) if isinstance(sections_json, str) else sections_json
            if student['section'] in sections:
                matching_instructors.append(instructor)
                print(f"  - {instructor['name']}: {instructor['course_name']} (Sections: {sections})")
        except Exception as e:
            print(f"  - Error parsing sections for {instructor['name']}: {e}")
    
    print(f"\nMatching instructors for section {student['section']}: {len(matching_instructors)}")
    
    # Get all unique courses
    all_courses = set()
    for course in courses_from_attendance:
        all_courses.add(course['course_name'])
    for instructor in matching_instructors:
        if instructor['course_name']:
            all_courses.add(instructor['course_name'])
    
    print(f"\nTotal unique courses: {len(all_courses)}")
    for course in sorted(all_courses):
        print(f"  - {course}")

else:
    print("No students found in database")

cursor.close()
conn.close()

print("\n" + "=" * 60)
