"""
Check student password
"""

import mysql.connector
import bcrypt

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

# Get STU001 user
cursor.execute("SELECT * FROM users WHERE username = 'STU001'")
user = cursor.fetchone()

if user:
    print(f"User: {user['username']}")
    print(f"Role: {user['role']}")
    print(f"Password hash: {user['password'][:50]}...")
    
    # Try common passwords
    test_passwords = ['password123', 'STU001', 'student', '123456']
    
    print("\nTesting passwords:")
    for pwd in test_passwords:
        try:
            if bcrypt.checkpw(pwd.encode('utf-8'), user['password'].encode('utf-8')):
                print(f"  ✅ '{pwd}' - MATCH!")
            else:
                print(f"  ❌ '{pwd}' - no match")
        except Exception as e:
            print(f"  ❌ '{pwd}' - error: {e}")
else:
    print("User not found")

cursor.close()
conn.close()
