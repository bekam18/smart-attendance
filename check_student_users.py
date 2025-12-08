"""
Check student user accounts
"""

import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("STUDENT USER ACCOUNTS")
print("=" * 60)

# Get students with user accounts
cursor.execute("""
    SELECT s.student_id, s.name, s.year, s.section, u.username, u.role
    FROM students s
    LEFT JOIN users u ON s.user_id = u.id
    WHERE u.role = 'student'
    LIMIT 10
""")

students = cursor.fetchall()

print(f"\nFound {len(students)} students with user accounts:")
for s in students:
    print(f"  - {s['student_id']}: {s['name']} (Username: {s['username']}, Year: {s['year']}, Section: {s['section']})")

cursor.close()
conn.close()

print("\n" + "=" * 60)
