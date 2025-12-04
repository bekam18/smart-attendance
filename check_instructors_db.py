"""Check instructors in database"""
import sys
sys.path.append('backend')

from db.mysql import get_db
import json

db = get_db()

print("=" * 60)
print("INSTRUCTORS IN DATABASE")
print("=" * 60)

instructors = db.execute_query("SELECT id, name, email, sections, courses FROM users WHERE role = 'instructor'")

for inst in instructors:
    print(f"\nID: {inst['id']}")
    print(f"Name: {inst['name']}")
    print(f"Email: {inst['email']}")
    
    try:
        sections = json.loads(inst['sections']) if inst['sections'] else []
        print(f"Sections: {sections}")
    except:
        print(f"Sections: None")
    
    try:
        courses = json.loads(inst['courses']) if inst['courses'] else []
        print(f"Courses: {courses}")
    except:
        print(f"Courses: None")

print("\n" + "=" * 60)
