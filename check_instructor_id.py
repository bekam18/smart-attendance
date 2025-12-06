import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING INSTRUCTOR IDS")
print("="*60 + "\n")

# Check instructor user
print("1. Checking instructor user:")
result = db.execute_query("SELECT id, username, name, role FROM users WHERE role = 'instructor'")
for user in result:
    print(f"   ID: {user['id']}, Username: {user['username']}, Name: {user['name']}")

# Check attendance records
print("\n2. Checking instructor_id in attendance:")
result = db.execute_query("SELECT DISTINCT instructor_id FROM attendance WHERE instructor_id IS NOT NULL")
print(f"   Distinct instructor_ids in attendance: {[r['instructor_id'] for r in result]}")

# Check specific attendance for Web course, Section A
print("\n3. Checking attendance for Web, Section A:")
result = db.execute_query("""
    SELECT instructor_id, COUNT(*) as count 
    FROM attendance 
    WHERE course_name = 'Web' AND section_id = 'A'
    GROUP BY instructor_id
""")
for row in result:
    print(f"   Instructor ID: {row['instructor_id']}, Records: {row['count']}")

# Check sessions
print("\n4. Checking instructor_id in sessions:")
result = db.execute_query("SELECT id, instructor_id, course_name, section_id FROM sessions WHERE course_name = 'Web' AND section_id = 'A'")
for session in result:
    print(f"   Session ID: {session['id']}, Instructor ID: {session['instructor_id']}, Course: {session['course_name']}, Section: {session['section_id']}")

print("\n" + "="*60 + "\n")
