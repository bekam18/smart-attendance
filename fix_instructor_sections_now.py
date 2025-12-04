"""Add sections to instructor"""
import sys
sys.path.append('backend')

from db.mysql import get_db
import json

db = get_db()

print("=" * 60)
print("FIXING INSTRUCTOR SECTIONS")
print("=" * 60)

# Get the instructor (bekam)
instructor = db.execute_query("SELECT id, name, email, sections FROM users WHERE email LIKE '%bekam%' OR name LIKE '%bekam%'")

if not instructor:
    print("\n❌ No instructor found with 'bekam' in name or email")
    print("\nSearching for any instructor...")
    instructor = db.execute_query("SELECT id, name, email, sections FROM users WHERE role = 'instructor' LIMIT 1")

if instructor:
    inst = instructor[0]
    print(f"\n✓ Found instructor:")
    print(f"  ID: {inst['id']}")
    print(f"  Name: {inst['name']}")
    print(f"  Email: {inst['email']}")
    
    current_sections = []
    if inst['sections']:
        try:
            current_sections = json.loads(inst['sections'])
        except:
            pass
    
    print(f"  Current sections: {current_sections}")
    
    # Add sections A, B, C if not present
    new_sections = ["A", "B", "C"]
    
    print(f"\n📝 Updating sections to: {new_sections}")
    
    db.execute_query(
        "UPDATE users SET sections = %s WHERE id = %s",
        (json.dumps(new_sections), inst['id'])
    )
    
    print("✓ Sections updated!")
    
    # Verify
    verify = db.execute_query("SELECT sections FROM users WHERE id = %s", (inst['id'],))
    if verify:
        sections = json.loads(verify[0]['sections'])
        print(f"✓ Verified sections: {sections}")
else:
    print("\n❌ No instructor found in database")

print("\n" + "=" * 60)
