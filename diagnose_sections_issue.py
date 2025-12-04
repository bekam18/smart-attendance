"""Complete diagnosis of sections issue"""
import sys
sys.path.append('backend')

from db.mysql import get_db
import json

db = get_db()

print("=" * 70)
print("COMPLETE SECTIONS DIAGNOSIS")
print("=" * 70)

# 1. Check all instructors
print("\n1. ALL INSTRUCTORS IN DATABASE:")
print("-" * 70)
instructors = db.execute_query("SELECT id, name, email, role, sections, courses FROM users WHERE role = 'instructor'")

for inst in instructors:
    print(f"\nID: {inst['id']}")
    print(f"Name: {inst['name']}")
    print(f"Email: {inst['email']}")
    
    try:
        sections = json.loads(inst['sections']) if inst['sections'] else []
        print(f"Sections: {sections}")
    except Exception as e:
        print(f"Sections: ERROR - {e}")
    
    try:
        courses = json.loads(inst['courses']) if inst['courses'] else []
        print(f"Courses: {courses}")
    except Exception as e:
        print(f"Courses: ERROR - {e}")

# 2. Check the specific user (bekam)
print("\n\n2. BEKAM USER DETAILS:")
print("-" * 70)
bekam = db.execute_query("SELECT * FROM users WHERE email = 'stu013@student.edu'")
if bekam:
    user = bekam[0]
    print(f"ID: {user['id']}")
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Sections (raw): {user.get('sections')}")
    print(f"Courses (raw): {user.get('courses')}")
    
    if user.get('sections'):
        try:
            sections = json.loads(user['sections'])
            print(f"Sections (parsed): {sections}")
        except Exception as e:
            print(f"Sections parse error: {e}")
    
    if user.get('courses'):
        try:
            courses = json.loads(user['courses'])
            print(f"Courses (parsed): {courses}")
        except Exception as e:
            print(f"Courses parse error: {e}")
else:
    print("❌ User not found!")

# 3. Test the API logic
print("\n\n3. SIMULATING API CALL:")
print("-" * 70)
if bekam:
    user_id = bekam[0]['id']
    print(f"User ID: {user_id}")
    
    # Simulate the API endpoint logic
    user_result = db.execute_query('SELECT sections FROM users WHERE id = %s', (user_id,))
    if user_result:
        print(f"Query result: {user_result[0]}")
        
        instructor_sections = []
        if user_result[0].get('sections'):
            try:
                instructor_sections = json.loads(user_result[0]['sections'])
                print(f"✓ Parsed sections: {instructor_sections}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"✗ Parse error: {e}")
        else:
            print("✗ No sections field in result")
        
        print(f"\nAPI would return: {{'sections': {instructor_sections}}}")

print("\n" + "=" * 70)
