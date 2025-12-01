"""
Update student information in database
- Group 1 (STU001-STU013): Section A, 4th Year
- Group 2 (STU014-STU020): Section B, 4th Year
- Fix STU020 name to "Yien"
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from db.mongo import init_db
from datetime import datetime

print("="*80)
print("UPDATING STUDENT INFORMATION")
print("="*80)

# Initialize and connect to database
print("\nConnecting to MongoDB...")
db = init_db()

if db is None:
    print("❌ Failed to connect to MongoDB")
    print("Make sure MongoDB is running!")
    sys.exit(1)

print("✅ Connected to database")

# Group 1: Section A, 4th Year (STU001-STU013)
group1_ids = [
    'STU001', 'STU002', 'STU003', 'STU004', 'STU005', 'STU006',
    'STU008', 'STU009', 'STU010', 'STU011', 'STU012', 'STU013'
]

# Group 2: Section B, 4th Year (STU014-STU019, STU021)
group2_ids = [
    'STU014', 'STU015', 'STU016', 'STU017', 'STU018', 'STU019', 'STU021'
]

print("\n[1] Updating Group 1 (Section A, 4th Year)...")
updated_count = 0
for student_id in group1_ids:
    result = db.students.update_one(
        {'student_id': student_id},
        {
            '$set': {
                'section': 'A',
                'year_level': '4th Year',
                'updated_at': datetime.utcnow()
            }
        }
    )
    if result.matched_count > 0:
        student = db.students.find_one({'student_id': student_id})
        print(f"  ✓ {student_id}: {student.get('name')} → Section A, 4th Year")
        updated_count += 1
    else:
        print(f"  ⚠ {student_id}: Not found in database")

print(f"\n  Updated {updated_count}/{len(group1_ids)} students in Group 1")

print("\n[2] Updating Group 2 (Section B, 4th Year)...")
updated_count = 0
for student_id in group2_ids:
    result = db.students.update_one(
        {'student_id': student_id},
        {
            '$set': {
                'section': 'B',
                'year_level': '4th Year',
                'updated_at': datetime.utcnow()
            }
        }
    )
    if result.matched_count > 0:
        student = db.students.find_one({'student_id': student_id})
        print(f"  ✓ {student_id}: {student.get('name')} → Section B, 4th Year")
        updated_count += 1
    else:
        print(f"  ⚠ {student_id}: Not found in database")

print(f"\n  Updated {updated_count}/{len(group2_ids)} students in Group 2")

print("\n[3] Fixing STU021 name to 'Yien'...")
result = db.students.update_one(
    {'student_id': 'STU021'},
    {
        '$set': {
            'name': 'Yien',
            'updated_at': datetime.utcnow()
        }
    }
)

if result.matched_count > 0:
    student = db.students.find_one({'student_id': 'STU021'})
    print(f"  ✓ STU021: Name updated to '{student.get('name')}'")
else:
    print(f"  ⚠ STU021: Not found in database")

print("\n[4] Verification - Listing all students...")
print("\n" + "="*80)
print("SECTION A (4th Year)")
print("="*80)
for student_id in sorted(group1_ids):
    student = db.students.find_one({'student_id': student_id})
    if student:
        print(f"{student_id}: {student.get('name'):20s} | Section: {student.get('section', 'N/A'):2s} | Year: {student.get('year_level', 'N/A')}")
    else:
        print(f"{student_id}: NOT FOUND")

print("\n" + "="*80)
print("SECTION B (4th Year)")
print("="*80)
for student_id in sorted(group2_ids):
    student = db.students.find_one({'student_id': student_id})
    if student:
        print(f"{student_id}: {student.get('name'):20s} | Section: {student.get('section', 'N/A'):2s} | Year: {student.get('year_level', 'N/A')}")
    else:
        print(f"{student_id}: NOT FOUND")

print("\n" + "="*80)
print("✓ UPDATE COMPLETE")
print("="*80)
