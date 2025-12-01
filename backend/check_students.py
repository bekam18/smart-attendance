"""Check students in database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pymongo import MongoClient

# Connect directly
client = MongoClient('mongodb://localhost:27017/')
db = client['smartattendance']

print("\n" + "="*80)
print("STUDENTS IN DATABASE")
print("="*80)

students = list(db.students.find({}, {'student_id': 1, 'name': 1, 'section': 1, 'year': 1}).limit(15))

for s in students:
    student_id = s.get('student_id', 'NO_ID')
    name = s.get('name', 'NO_NAME')
    section = s.get('section', 'MISSING')
    year = s.get('year', 'MISSING')
    print(f"{student_id:10} | {name:25} | Section: {section:5} | Year: {year}")

print("="*80)
print(f"\nTotal students: {db.students.count_documents({})}")

section_a_count = db.students.count_documents({'section': 'A', 'year': '4th Year'})
print(f"Students in Section A, 4th Year: {section_a_count}")

if section_a_count == 0:
    print("\n⚠️  NO STUDENTS FOUND IN SECTION A, 4TH YEAR!")
    print("This is why absent marking found 0 students.")
    print("\nYou need to update your students with section and year fields.")
    print("Run: update_all_students_year.bat")

print()
