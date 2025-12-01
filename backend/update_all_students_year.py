"""
Update all students in database to 4th Year
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from db.mongo import init_db
from datetime import datetime

print("="*80)
print("UPDATE ALL STUDENTS TO 4TH YEAR")
print("="*80)

# Initialize and connect to database
print("\nConnecting to MongoDB...")
db = init_db()

if db is None:
    print("❌ Failed to connect to MongoDB")
    print("Make sure MongoDB is running!")
    sys.exit(1)

print("✅ Connected to database")

# Update all students to 4th Year with sections
print("\nUpdating all students to 4th Year with sections...")

# Get all students
all_students = list(db.students.find({}, {'student_id': 1}))
total = len(all_students)

# Assign sections: first half to A, second half to B
half = total // 2

updated = 0
for i, student in enumerate(all_students):
    section = 'A' if i < half else 'B'
    db.students.update_one(
        {'_id': student['_id']},
        {
            '$set': {
                'year': '4th Year',  # Use 'year' not 'year_level'
                'section': section,
                'updated_at': datetime.utcnow()
            }
        }
    )
    updated += 1

result_modified = updated

print(f"\n✅ Updated {result_modified} students to 4th Year with sections")

# Verify the update
print("\nVerifying update...")
students = list(db.students.find({}, {'student_id': 1, 'name': 1, 'year': 1, 'section': 1}).sort('student_id', 1))

print("\n" + "="*80)
print("ALL STUDENTS")
print("="*80)
for student in students:
    year = student.get('year', 'N/A')
    section = student.get('section', 'N/A')
    print(f"{student.get('student_id')}: {student.get('name'):20s} | Year: {year:10s} | Section: {section}")

print("\n" + "="*80)
print("✓ UPDATE COMPLETE")
print("="*80)
print(f"Total students: {len(students)}")
print(f"All students are now in 4th Year")
print("="*80)
