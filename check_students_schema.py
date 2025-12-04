"""Check students table schema"""
import sys
sys.path.append('backend')

from db.mysql import get_db

db = get_db()

print("=" * 60)
print("STUDENTS TABLE SCHEMA")
print("=" * 60)

# Get table structure
schema = db.execute_query("DESCRIBE students")

for column in schema:
    print(f"{column['Field']:20} {column['Type']:20} {column['Null']:5} {column['Key']:5} {column['Default']}")

print("\n" + "=" * 60)
print("SAMPLE STUDENT DATA")
print("=" * 60)

students = db.execute_query("SELECT * FROM students LIMIT 3")
if students:
    for student in students:
        print(f"\nStudent: {student}")
