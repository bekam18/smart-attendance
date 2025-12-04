"""
Verify that absent students in attendance records are from the correct section
"""

from db.mysql import get_db
from datetime import date, datetime, timedelta

def verify_absent_students_section():
    print("\n" + "="*70)
    print("VERIFYING ABSENT STUDENTS ARE FROM CORRECT SECTION")
    print("="*70)
    
    db = get_db()
    
    # Get recent sessions with absent students
    recent_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    
    print(f"\nChecking sessions from {recent_date} onwards...")
    print("-" * 70)
    
    sessions = db.execute_query(
        '''SELECT id, name, section_id, year, start_time, status 
           FROM sessions 
           WHERE start_time >= %s
           ORDER BY start_time DESC''',
        (recent_date,)
    )
    
    if not sessions:
        print("\n⚠️  No recent sessions found")
        print("   Start a session and click 'Stop Camera' to test")
        return
    
    total_issues = 0
    
    for session in sessions:
        session_id = session['id']
        session_section = session['section_id']
        session_year = session['year']
        
        print(f"\n📋 Session: {session['name']}")
        print(f"   ID: {session_id}")
        print(f"   Section: {session_section}, Year: {session_year}")
        print(f"   Status: {session['status']}")
        
        # Get all attendance records for this session
        attendance = db.execute_query(
            '''SELECT a.student_id, a.status, s.section, s.year, s.name as student_name
               FROM attendance a
               JOIN students s ON a.student_id = s.student_id
               WHERE a.session_id = %s
               ORDER BY a.status, a.student_id''',
            (session_id,)
        )
        
        if not attendance:
            print("   ℹ️  No attendance records yet")
            continue
        
        # Separate present and absent
        present = [a for a in attendance if a['status'] == 'present']
        absent = [a for a in attendance if a['status'] == 'absent']
        
        print(f"   Present: {len(present)}, Absent: {len(absent)}")
        
        # Check each absent student
        session_issues = 0
        for record in absent:
            student_section = record['section']
            student_year = record['year']
            student_id = record['student_id']
            student_name = record['student_name']
            
            # Check if student is from the correct section
            if student_section != session_section or student_year != session_year:
                print(f"\n   ❌ MISMATCH FOUND:")
                print(f"      Student: {student_name} ({student_id})")
                print(f"      Student Section/Year: {student_section}, {student_year}")
                print(f"      Session Section/Year: {session_section}, {session_year}")
                print(f"      Status: {record['status']}")
                session_issues += 1
                total_issues += 1
        
        if session_issues == 0 and absent:
            print(f"   ✅ All {len(absent)} absent students are from correct section")
        
        # Show sample of absent students
        if absent and session_issues == 0:
            print(f"\n   Sample absent students:")
            for record in absent[:3]:
                print(f"      - {record['student_name']} ({record['student_id']}) - Section {record['section']}, Year {record['year']}")
            if len(absent) > 3:
                print(f"      ... and {len(absent) - 3} more")
    
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    if total_issues == 0:
        print("\n✅ SUCCESS: All absent students are from the correct section!")
        print("   The absent marking feature is working correctly.")
    else:
        print(f"\n❌ ISSUES FOUND: {total_issues} mismatched records")
        print("   Some absent students are from wrong sections.")
        print("   This needs to be fixed!")
    
    print("\n" + "="*70)
    print("HOW TO TEST")
    print("="*70)
    print("\n1. Login as instructor")
    print("2. Start a session for 'Section A, 4th Year'")
    print("3. Let 2-3 students get recognized")
    print("4. Click 'Stop Camera' button")
    print("5. Go to 'Attendance Records'")
    print("6. Check that absent students shown are from Section A, 4th Year")
    print("7. Run this script again to verify")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    try:
        verify_absent_students_section()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
