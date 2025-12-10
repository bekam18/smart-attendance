"""Check STU001 section and year"""
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

print("="*80)
print("CHECKING STU001 (NABILA)")
print("="*80)

# Check STU001 in students table
cursor.execute("SELECT * FROM students WHERE student_id = 'STU001'")
student = cursor.fetchone()

if student:
    print(f"\n✓ Found STU001 in students table:")
    print(f"  Name: {student['name']}")
    print(f"  Section: {student['section']}")
    print(f"  Year: {student['year']}")
    print(f"  Department: {student['department']}")
else:
    print("\n❌ STU001 not found in students table!")

# Check the active session
print("\n" + "="*80)
print("CHECKING ACTIVE SESSION")
print("="*80)

cursor.execute("SELECT * FROM sessions WHERE status = 'active' ORDER BY start_time DESC LIMIT 1")
session = cursor.fetchone()

if session:
    print(f"\n✓ Found active session:")
    print(f"  ID: {session['id']}")
    print(f"  Name: {session['name']}")
    print(f"  Section: {session['section_id']}")
    print(f"  Year: {session['year']}")
    print(f"  Instructor: {session['instructor_name']}")
    
    # Check if STU001 matches this session
    if student:
        print("\n" + "="*80)
        print("SECTION/YEAR MATCH CHECK")
        print("="*80)
        
        student_section = student['section']
        student_year = student['year']
        session_section = session['section_id']
        session_year = session['year']
        
        print(f"\nStudent STU001:")
        print(f"  Section: '{student_section}'")
        print(f"  Year: '{student_year}'")
        
        print(f"\nActive Session:")
        print(f"  Section: '{session_section}'")
        print(f"  Year: '{session_year}'")
        
        if student_section == session_section and student_year == session_year:
            print("\n✅ MATCH - STU001 should appear in attendance list")
        else:
            print("\n❌ MISMATCH - STU001 will NOT appear in attendance list")
            print("\nTo fix, update STU001 to match session:")
            print(f"  UPDATE students SET section = '{session_section}', year = '{session_year}' WHERE student_id = 'STU001';")
else:
    print("\n⚠️ No active session found")

# Check all students in the session's section/year
if session:
    print("\n" + "="*80)
    print(f"ALL STUDENTS IN SECTION {session['section_id']}, YEAR {session['year']}")
    print("="*80)
    
    cursor.execute(
        "SELECT student_id, name, section, year FROM students WHERE section = %s AND year = %s",
        (session['section_id'], session['year'])
    )
    students = cursor.fetchall()
    
    print(f"\nFound {len(students)} students:")
    for s in students:
        print(f"  - {s['student_id']}: {s['name']} (Section {s['section']}, {s['year']})")

cursor.close()
db.close()

print("\n" + "="*80)
print("CHECK COMPLETE")
print("="*80)
