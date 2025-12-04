"""
Diagnose why absent marking returns 0 students
"""

from db.mysql import get_db
from datetime import date

def diagnose_absent_marking(session_id):
    print("\n" + "="*70)
    print(f"DIAGNOSING ABSENT MARKING FOR SESSION {session_id}")
    print("="*70)
    
    db = get_db()
    
    # Get session info
    print("\n1. SESSION INFO:")
    print("-" * 70)
    session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
    if not session_result:
        print(f"❌ Session {session_id} not found!")
        return
    
    session = session_result[0]
    print(f"Session ID: {session['id']}")
    print(f"Name: {session.get('name')}")
    print(f"Section: '{session.get('section_id')}'")
    print(f"Year: '{session.get('year')}'")
    print(f"Status: {session.get('status')}")
    
    # Get all students in database
    print("\n2. ALL STUDENTS IN DATABASE:")
    print("-" * 70)
    all_students = db.execute_query('SELECT student_id, name, section, year FROM students')
    
    sections = {}
    for student in all_students:
        key = f"Section {student['section']}, Year {student['year']}"
        if key not in sections:
            sections[key] = []
        sections[key].append(student)
    
    for key, students in sections.items():
        print(f"\n{key}: {len(students)} students")
        for s in students[:3]:
            print(f"  - {s['student_id']}: {s['name']}")
        if len(students) > 3:
            print(f"  ... and {len(students) - 3} more")
    
    # Try to find students with session's section/year
    print("\n3. STUDENTS MATCHING SESSION SECTION/YEAR:")
    print("-" * 70)
    print(f"Looking for: section = '{session.get('section_id')}' AND year = '{session.get('year')}'")
    
    matching_students = db.execute_query(
        'SELECT student_id, name, section, year FROM students WHERE section = %s AND year = %s',
        (session.get('section_id'), session.get('year'))
    )
    
    if not matching_students:
        print("❌ NO STUDENTS FOUND!")
        print("\nPossible reasons:")
        print("1. Session section/year doesn't match any students")
        print("2. Section/year format mismatch (e.g., 'A' vs 'sectionA', '4' vs '4th Year')")
        print("3. No students in database for this section/year")
    else:
        print(f"✅ Found {len(matching_students)} students:")
        for s in matching_students:
            print(f"  - {s['student_id']}: {s['name']} (Section {s['section']}, Year {s['year']})")
    
    # Get present students
    print("\n4. PRESENT STUDENTS IN THIS SESSION:")
    print("-" * 70)
    today = date.today().isoformat()
    present_students = db.execute_query(
        'SELECT DISTINCT student_id FROM attendance WHERE session_id = %s AND date = %s',
        (session_id, today)
    )
    
    if not present_students:
        print("No students marked present yet")
    else:
        print(f"Found {len(present_students)} present students:")
        for s in present_students:
            print(f"  - {s['student_id']}")
    
    # Calculate who should be marked absent
    print("\n5. WHO SHOULD BE MARKED ABSENT:")
    print("-" * 70)
    if not matching_students:
        print("❌ Cannot mark absent - no students found in section/year")
    else:
        present_ids = [s['student_id'] for s in present_students] if present_students else []
        absent_students = [s for s in matching_students if s['student_id'] not in present_ids]
        
        print(f"Total students in section: {len(matching_students)}")
        print(f"Present students: {len(present_ids)}")
        print(f"Should mark absent: {len(absent_students)}")
        
        if absent_students:
            print("\nStudents to mark absent:")
            for s in absent_students:
                print(f"  - {s['student_id']}: {s['name']}")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    print("="*70)
    
    if not matching_students:
        print("\n❌ PROBLEM: No students found matching session section/year")
        print("\nFIX OPTIONS:")
        print("1. Update session section/year to match students:")
        print(f"   Current: section='{session.get('section_id')}', year='{session.get('year')}'")
        print("   Available sections/years:")
        for key in sections.keys():
            print(f"   - {key}")
        print("\n2. Update students' section/year to match session")
        print("\n3. Check for format mismatches:")
        print("   - 'A' vs 'sectionA'")
        print("   - '4' vs '4th Year'")
        print("   - '4th Year' vs '4'")
    else:
        print("\n✅ System is working correctly!")
        print(f"   Will mark {len(absent_students) if matching_students else 0} students as absent")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python diagnose_absent_marking.py <session_id>")
        print("\nOr run without arguments to check latest session:")
        db = get_db()
        sessions = db.execute_query('SELECT id, name, section_id, year FROM sessions ORDER BY start_time DESC LIMIT 5')
        print("\nRecent sessions:")
        for s in sessions:
            print(f"  ID: {s['id']} - {s['name']} (Section {s['section_id']}, Year {s['year']})")
        if sessions:
            print(f"\nDiagnosing latest session (ID: {sessions[0]['id']})...")
            diagnose_absent_marking(sessions[0]['id'])
    else:
        session_id = sys.argv[1]
        diagnose_absent_marking(session_id)
