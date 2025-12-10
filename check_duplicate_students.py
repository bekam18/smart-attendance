"""Check for duplicate students in Section A, Year 4"""
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

print("="*80)
print("CHECKING STUDENTS IN SECTION A, YEAR 4")
print("="*80)

# Get all students in Section A, Year 4
cursor.execute("""
    SELECT student_id, name, section, year, email
    FROM students 
    WHERE section = 'A' AND year = '4'
    ORDER BY student_id
""")
students = cursor.fetchall()

print(f"\n✓ Found {len(students)} students in Section A, Year 4:")
for s in students:
    print(f"  - {s['student_id']}: {s['name']} (Section {s['section']}, Year {s['year']})")

# Check for duplicates by student_id
print("\n" + "="*80)
print("CHECKING FOR DUPLICATE STUDENT IDs")
print("="*80)

cursor.execute("""
    SELECT student_id, COUNT(*) as count
    FROM students
    WHERE section = 'A' AND year = '4'
    GROUP BY student_id
    HAVING count > 1
""")
duplicates = cursor.fetchall()

if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate student IDs:")
    for dup in duplicates:
        print(f"  - {dup['student_id']}: {dup['count']} records")
else:
    print("\n✅ No duplicate student IDs found")

# Check for students with wrong year format
print("\n" + "="*80)
print("CHECKING FOR WRONG YEAR FORMATS IN SECTION A")
print("="*80)

cursor.execute("""
    SELECT student_id, name, section, year
    FROM students
    WHERE section = 'A' AND year != '4'
    ORDER BY year, student_id
""")
wrong_year = cursor.fetchall()

if wrong_year:
    print(f"\n⚠️ Found {len(wrong_year)} students in Section A with different years:")
    for s in wrong_year:
        print(f"  - {s['student_id']}: {s['name']} (Section {s['section']}, Year '{s['year']}')")
else:
    print("\n✅ No students with wrong year format")

# Check total students in Section A (all years)
print("\n" + "="*80)
print("ALL STUDENTS IN SECTION A (ALL YEARS)")
print("="*80)

cursor.execute("""
    SELECT year, COUNT(*) as count
    FROM students
    WHERE section = 'A'
    GROUP BY year
    ORDER BY year
""")
all_section_a = cursor.fetchall()

print(f"\nSection A breakdown by year:")
total = 0
for row in all_section_a:
    print(f"  - Year '{row['year']}': {row['count']} students")
    total += row['count']
print(f"\nTotal in Section A: {total} students")

# Check the active session
print("\n" + "="*80)
print("CHECKING ACTIVE SESSION")
print("="*80)

cursor.execute("SELECT * FROM sessions WHERE status = 'active' ORDER BY start_time DESC LIMIT 1")
session = cursor.fetchone()

if session:
    print(f"\n✓ Active session:")
    print(f"  ID: {session['id']}")
    print(f"  Name: {session['name']}")
    print(f"  Section: {session['section_id']}")
    print(f"  Year: {session['year']}")
    
    # Check how many students would be marked absent
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM students
        WHERE section = %s AND year = %s
    """, (session['section_id'], session['year']))
    
    result = cursor.fetchone()
    print(f"\n  Students that would be marked: {result['count']}")
    
    # Check how many are already present
    from datetime import date
    today = date.today().isoformat()
    
    cursor.execute("""
        SELECT COUNT(DISTINCT student_id) as count
        FROM attendance
        WHERE session_id = %s AND date = %s AND status = 'present'
    """, (session['id'], today))
    
    present = cursor.fetchone()
    print(f"  Already marked present: {present['count']}")
    print(f"  Would mark absent: {result['count'] - present['count']}")

cursor.close()
db.close()

print("\n" + "="*80)
print("CHECK COMPLETE")
print("="*80)
