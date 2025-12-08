"""Check student user passwords"""
import mysql.connector
import bcrypt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

# Get student users
cursor.execute("""
    SELECT u.id, u.username, u.name, u.password, s.student_id
    FROM users u
    LEFT JOIN students s ON u.id = s.user_id
    WHERE u.username IN ('STU001', 'STU002')
    OR s.student_id IN ('STU001', 'STU002')
""")
users = cursor.fetchall()

print("="*80)
print("STUDENT USER PASSWORD CHECK")
print("="*80)

if not users:
    print("\n⚠️ No users found with usernames STU001 or STU002")
    print("\nLet me check all student users:")
    cursor.execute("""
        SELECT u.id, u.username, u.name, u.role, s.student_id
        FROM users u
        LEFT JOIN students s ON u.id = s.user_id
        WHERE u.role = 'student'
        LIMIT 10
    """)
    all_students = cursor.fetchall()
    for student in all_students:
        print(f"  - Username: {student['username']}, Name: {student['name']}, Student ID: {student.get('student_id')}")
else:
    test_passwords = {
        "STU001": ["Nabil123", "nabil123", "student123"],
        "STU002": ["Nardos123", "nardos123", "student123"]
    }

    for user in users:
        print(f"\n{'='*80}")
        print(f"User: {user['name']} (Username: {user['username']}, Student ID: {user.get('student_id')})")
        print(f"{'='*80}")
        
        stored_hash = user['password']
        print(f"Stored hash: {stored_hash[:50]}...")
        
        # Test different passwords
        print("\nTesting passwords:")
        username = user.get('student_id') or user['username']
        for test_pass in test_passwords.get(username, ["student123", "Nabil123", "Nardos123"]):
            try:
                if bcrypt.checkpw(test_pass.encode('utf-8'), stored_hash.encode('utf-8')):
                    print(f"  ✅ '{test_pass}' - CORRECT PASSWORD!")
                else:
                    print(f"  ❌ '{test_pass}' - Wrong")
            except Exception as e:
                print(f"  ⚠️ '{test_pass}' - Error: {e}")

cursor.close()
db.close()

print("\n" + "="*80)
print("CHECK COMPLETE")
print("="*80)
