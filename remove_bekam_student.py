import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("Student to be removed:")
student = db.execute_query("SELECT * FROM students WHERE student_id = 'STU013'")[0]
print(f"Student ID: {student['student_id']}")
print(f"Name: {student['name']}")
print(f"Year: {student['year']}")
print(f"Section: {student['section']}")

# Uncomment the lines below to remove the student
# # First remove attendance records
# db.execute_query("DELETE FROM attendance WHERE student_id = 'STU013'", fetch=False)
# # Then remove student record
# db.execute_query("DELETE FROM students WHERE student_id = 'STU013'", fetch=False)
# # Finally remove user account
# user_id = student['user_id']
# db.execute_query("DELETE FROM users WHERE id = %s", (user_id,), fetch=False)
# print("\n✅ Bekam Ayele has been removed from the system")

print("\n⚠️  To remove this student, uncomment the delete lines in this script")
