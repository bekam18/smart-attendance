#!/usr/bin/env python3
"""Test student courses assignment fix"""

import sys
import requests
import json
sys.path.append('backend')

def test_student_courses():
    """Test that students only see courses assigned to their year"""
    
    print("Testing Student Courses Assignment Fix")
    print("=" * 40)
    
    # Test with a sample student login
    base_url = "http://127.0.0.1:5000/api"
    
    # First, let's check what students exist in the database
    try:
        from db.mysql import get_db
        db = get_db()
        
        # Get a sample student
        students = db.execute_query("SELECT * FROM students LIMIT 5")
        print(f"📊 Found {len(students)} students in database:")
        
        for student in students:
            print(f"   - {student['name']} (ID: {student['student_id']}, Year: {student.get('year', 'N/A')}, Section: {student.get('section', 'N/A')})")
        
        if not students:
            print("❌ No students found in database")
            return
        
        # Get instructors and their course assignments
        instructors = db.execute_query("SELECT name, course_name, class_year, sections FROM users WHERE role = 'instructor'")
        print(f"\n📚 Found {len(instructors)} instructors:")
        
        for instructor in instructors:
            sections = instructor.get('sections', 'N/A')
            if sections and sections != 'N/A':
                try:
                    sections = json.loads(sections) if isinstance(sections, str) else sections
                    sections = ', '.join(sections) if isinstance(sections, list) else str(sections)
                except:
                    pass
            print(f"   - {instructor['name']}: {instructor.get('course_name', 'N/A')} (Year: {instructor.get('class_year', 'N/A')}, Sections: {sections})")
        
        # Test the profile endpoint logic directly
        sample_student = students[0]
        student_year = sample_student.get('year', '')
        student_section = sample_student.get('section', 'A')
        
        print(f"\n🔍 Testing profile logic for student: {sample_student['name']}")
        print(f"   Student Year: {student_year}")
        print(f"   Student Section: {student_section}")
        
        # Normalize year format
        year_normalized = student_year.replace('th Year', '').replace('st Year', '').replace('nd Year', '').replace('rd Year', '').strip()
        
        # Get instructors for this student's year
        instructor_query = """
            SELECT DISTINCT u.id, u.name, u.course_name, u.sections, u.class_year 
            FROM users u 
            WHERE u.role = 'instructor' AND (u.class_year = %s OR u.class_year = %s)
        """
        matching_instructors = db.execute_query(instructor_query, (student_year, year_normalized))
        
        print(f"\n📋 Instructors matching student's year ({student_year} or {year_normalized}):")
        assigned_courses = []
        
        for instructor in matching_instructors:
            course_name = instructor.get('course_name', '')
            sections_json = instructor.get('sections', None)
            
            if course_name:
                if sections_json:
                    try:
                        sections = json.loads(sections_json) if isinstance(sections_json, str) else sections_json
                        if student_section in sections:
                            assigned_courses.append(course_name)
                            print(f"   ✅ {instructor['name']}: {course_name} (teaches section {student_section})")
                        else:
                            print(f"   ❌ {instructor['name']}: {course_name} (doesn't teach section {student_section}, teaches: {sections})")
                    except Exception as e:
                        print(f"   ⚠️  {instructor['name']}: {course_name} (section parsing error: {e})")
                else:
                    assigned_courses.append(course_name)
                    print(f"   ✅ {instructor['name']}: {course_name} (no section restriction)")
        
        assigned_courses = list(set(assigned_courses))
        assigned_courses.sort()
        
        print(f"\n🎯 Final assigned courses for {sample_student['name']}: {assigned_courses}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing student courses: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_student_courses()