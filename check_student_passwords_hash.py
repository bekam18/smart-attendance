"""Check student passwords in database"""
import mysql.connector
import bcrypt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

# Get students
cursor.execute("SELECT student_id, name, password FROM students WHERE student_id IN ('STU001', 'STU002')")
students = cursor.fetchall()

print("="*80)
print("STUDENT PASSWORD CHECK")
print("="*80)

test_passwords = {
    "STU001": ["Nabil123", "nabil123", "student123"],
    "STU002": ["Nardos123", "nardos123", "student123"]
}

for student in students:
    print(f"\n{'='*80}")
    print(f"Student: {student['name']} ({student['student_id']})")
    print(f"{'='*80}")
    
    stored_hash = student['password']
    print(f"Stored hash: {stored_hash[:50]}...")
    
    # Test different passwords
    print("\nTesting passwords:")
    for test_pass in test_passwords.get(student['student_id'], []):
        try:
            if bcrypt.checkpw(test_pass.encode('utf-8'), stored_hash.encode('utf-8')):
                print(f"  ✅ '{test_pass}' - CORRECT")
            else:
                print(f"  ❌ '{test_pass}' - Wrong")
        except Exception as e:
            print(f"  ⚠️ '{test_pass}' - Error: {e}")

cursor.close()
db.close()

print("\n" + "="*80)
print("CHECK COMPLETE")
print("="*80)
