import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING COURSES TABLE")
print("="*60 + "\n")

# Check if courses table exists
result = db.execute_query("SHOW TABLES LIKE 'courses'")
if result:
    print("✅ Courses table exists\n")
    
    # Get table structure
    schema = db.execute_query("DESCRIBE courses")
    print("Courses table columns:")
    for col in schema:
        print(f"  - {col['Field']:20} {col['Type']:20}")
    
    # Count records
    count = db.execute_query("SELECT COUNT(*) as count FROM courses")
    print(f"\nTotal courses: {count[0]['count']}")
    
    # Show sample
    if count[0]['count'] > 0:
        sample = db.execute_query("SELECT * FROM courses LIMIT 5")
        print("\nSample courses:")
        for c in sample:
            print(f"  ID: {c.get('id')}, Name: {c.get('name') or c.get('course_name')}, Code: {c.get('code') or c.get('course_code')}")
else:
    print("❌ Courses table does NOT exist")
    print("\nNote: Course information is stored in sessions.course_name")
    print("Checking sessions table for course data...")
    result = db.execute_query("SELECT DISTINCT course_name FROM sessions")
    print(f"\nCourses in sessions table:")
    for r in result:
        print(f"  - {r['course_name']}")

print("\n" + "="*60 + "\n")
