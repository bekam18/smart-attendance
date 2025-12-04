"""Check which sections have students in each course"""
import sys
sys.path.append('backend')

from db.mysql import get_db

db = get_db()

print("=" * 60)
print("CHECKING SECTIONS BY COURSE")
print("=" * 60)

# Get all courses
courses_query = "SELECT DISTINCT course_name FROM students WHERE enabled = 1 ORDER BY course_name"
courses = db.execute_query(courses_query)

print(f"\nFound {len(courses)} courses with enabled students:\n")

for course in courses:
    course_name = course['course_name']
    print(f"\n📚 Course: {course_name}")
    print("-" * 40)
    
    # Get sections for this course
    sections_query = """
        SELECT DISTINCT section, COUNT(*) as student_count
        FROM students 
        WHERE course_name = %s AND enabled = 1
        GROUP BY section
        ORDER BY section
    """
    sections = db.execute_query(sections_query, (course_name,))
    
    if sections:
        for section in sections:
            print(f"   Section {section['section']}: {section['student_count']} students")
    else:
        print("   No sections found")

print("\n" + "=" * 60)
print("CHECKING INSTRUCTOR SECTIONS")
print("=" * 60)

# Get instructor info
instructor_query = "SELECT id, name, sections, courses FROM users WHERE role = 'instructor'"
instructors = db.execute_query(instructor_query)

import json

for instructor in instructors:
    print(f"\n👨‍🏫 Instructor: {instructor['name']} (ID: {instructor['id']})")
    
    # Parse sections
    try:
        assigned_sections = json.loads(instructor['sections']) if instructor['sections'] else []
        print(f"   Assigned Sections: {assigned_sections}")
    except:
        assigned_sections = []
        print(f"   Assigned Sections: None")
    
    # Parse courses
    try:
        assigned_courses = json.loads(instructor['courses']) if instructor['courses'] else []
        print(f"   Assigned Courses: {assigned_courses}")
    except:
        assigned_courses = []
        print(f"   Assigned Courses: None")
    
    # For each course, check which sections have students
    for course in assigned_courses:
        print(f"\n   Course: {course}")
        if assigned_sections:
            placeholders = ','.join(['%s'] * len(assigned_sections))
            query = f"""
                SELECT DISTINCT section, COUNT(*) as count
                FROM students 
                WHERE course_name = %s 
                AND section IN ({placeholders})
                AND enabled = 1
                GROUP BY section
                ORDER BY section
            """
            params = [course] + assigned_sections
            sections = db.execute_query(query, params)
            
            if sections:
                for section in sections:
                    print(f"      ✓ Section {section['section']}: {section['count']} students")
            else:
                print(f"      ✗ No students found in assigned sections for this course")

print("\n" + "=" * 60)
