"""Fix the correct instructor (be@gmail.com)"""
import sys
sys.path.append('backend')

from db.mysql import get_db
import json

db = get_db()

print("=" * 60)
print("FIXING INSTRUCTOR: be@gmail.com")
print("=" * 60)

# Update the instructor with sections
sections = ["A", "B", "C"]

db.execute_query(
    "UPDATE users SET sections = %s WHERE email = 'be@gmail.com' AND role = 'instructor'",
    (json.dumps(sections),)
)

print(f"\n✓ Updated sections to: {sections}")

# Verify
result = db.execute_query("SELECT id, name, email, sections, courses FROM users WHERE email = 'be@gmail.com'")
if result:
    user = result[0]
    print(f"\n✓ Verified:")
    print(f"  ID: {user['id']}")
    print(f"  Name: {user['name']}")
    print(f"  Email: {user['email']}")
    print(f"  Sections: {json.loads(user['sections'])}")
    print(f"  Courses: {json.loads(user['courses']) if user['courses'] else []}")

print("\n" + "=" * 60)
