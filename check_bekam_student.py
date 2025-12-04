import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

# Check for Bekam Ayele
students = db.execute_query("SELECT student_id, name, year, section FROM students WHERE name LIKE '%Bekam%'")

print("=" * 60)
print("Students with 'Bekam' in name:")
print("=" * 60)

for s in students:
    print(f"Student ID: {s['student_id']}")
    print(f"Name: {s['name']}")
    print(f"Year: {s.get('year', 'N/A')}")
    print(f"Section: {s.get('section', 'N/A')}")
    print("-" * 60)

# Check all Section A, 4th Year students
print("\n" + "=" * 60)
print("All Section A, 4th Year students:")
print("=" * 60)

section_a_students = db.execute_query("SELECT student_id, name, year, section FROM students WHERE section = 'A' AND year = '4th Year'")

for s in section_a_students:
    print(f"ID: {s['student_id']}, Name: {s['name']}")

print(f"\nTotal: {len(section_a_students)} students")
