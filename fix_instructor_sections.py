import mysql.connector
import json

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

# Get all instructors
cursor.execute("SELECT id, username FROM users WHERE role = 'instructor'")
instructors = cursor.fetchall()

print("=== UPDATING INSTRUCTOR SECTIONS ===\n")

# Assign sections A and B to all instructors
sections = ['A', 'B']
sections_json = json.dumps(sections)

for instructor in instructors:
    cursor.execute(
        "UPDATE users SET sections = %s WHERE id = %s",
        (sections_json, instructor['id'])
    )
    print(f"✓ Updated {instructor['username']} with sections: {sections}")

conn.commit()
print(f"\n✓ Successfully updated {len(instructors)} instructors")

# Verify
cursor.execute("SELECT id, username, sections FROM users WHERE role = 'instructor'")
instructors = cursor.fetchall()

print("\n=== VERIFICATION ===\n")
for instructor in instructors:
    sections = json.loads(instructor['sections']) if instructor['sections'] else []
    print(f"{instructor['username']}: {sections}")

cursor.close()
conn.close()
