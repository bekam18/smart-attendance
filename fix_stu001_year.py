"""Fix STU001 year format to match session"""
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor()

print("="*80)
print("FIXING STU001 YEAR FORMAT")
print("="*80)

# Update STU001 year from '4th Year' to '4'
print("\n→ Updating STU001 year from '4th Year' to '4'...")
cursor.execute("UPDATE students SET year = '4' WHERE student_id = 'STU001'")
db.commit()

print("✅ STU001 year updated successfully!")

# Verify
cursor.execute("SELECT student_id, name, section, year FROM students WHERE student_id = 'STU001'")
student = cursor.fetchone()

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)
print(f"\nSTU001 (Nabila):")
print(f"  Section: {student[2]}")
print(f"  Year: {student[3]}")

print("\n✅ STU001 will now appear in attendance list when Stop Camera is clicked")

cursor.close()
db.close()

print("\n" + "="*80)
print("FIX COMPLETE")
print("="*80)
