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

from db.mysql import get_db
from datetime import datetime

print("="*80)
print("UPDATING STUDENT INFORMATION")
print("="*80)

# Initialize and connect to database
print("\nConnecting to MySQL...")
db = get_db()

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
    rows_affected = db.execute_query(
        'UPDATE students SET section = %s, year = %s, updated_at = %s WHERE student_id = %s',
        ('A', '4th Year', datetime.utcnow(), student_id),
        fetch=False
    )
    if rows_affected > 0:
        student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (student_id,))
        student = student_result[0] if student_result else None
        if student:
            print(f"  ✓ {student_id}: {student.get('name')} → Section A, 4th Year")
        updated_count += 1
    else:
        print(f"  ⚠ {student_id}: Not found in database")

print(f"\n  Updated {updated_count}/{len(group1_ids)} students in Group 1")

print("\n[2] Updating Group 2 (Section B, 4th Year)...")
updated_count = 0
for student_id in group2_ids:
    rows_affected = db.execute_query(
        'UPDATE students SET section = %s, year = %s, updated_at = %s WHERE student_id = %s',
        ('B', '4th Year', datetime.utcnow(), student_id),
        fetch=False
    )
    if rows_affected > 0:
        student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (student_id,))
        student = student_result[0] if student_result else None
        if student:
            print(f"  ✓ {student_id}: {student.get('name')} → Section B, 4th Year")
        updated_count += 1
    else:
        print(f"  ⚠ {student_id}: Not found in database")

print(f"\n  Updated {updated_count}/{len(group2_ids)} students in Group 2")

print("\n[3] Fixing STU021 name to 'Yien'...")
rows_affected = db.execute_query(
    'UPDATE students SET name = %s, updated_at = %s WHERE student_id = %s',
    ('Yien', datetime.utcnow(), 'STU021'),
    fetch=False
)

if rows_affected > 0:
    student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', ('STU021',))
    student = student_result[0] if student_result else None
    if student:
        print(f"  ✓ STU021: Name updated to '{student.get('name')}'")
else:
    print(f"  ⚠ STU021: Not found in database")

print("\n[4] Verification - Listing all students...")
print("\n" + "="*80)
print("SECTION A (4th Year)")
print("="*80)
for student_id in sorted(group1_ids):
    student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (student_id,))
    student = student_result[0] if student_result else None
    if student:
        print(f"{student_id}: {student.get('name'):20s} | Section: {student.get('section', 'N/A'):2s} | Year: {student.get('year', 'N/A')}")
    else:
        print(f"{student_id}: NOT FOUND")

print("\n" + "="*80)
print("SECTION B (4th Year)")
print("="*80)
for student_id in sorted(group2_ids):
    student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (student_id,))
    student = student_result[0] if student_result else None
    if student:
        print(f"{student_id}: {student.get('name'):20s} | Section: {student.get('section', 'N/A'):2s} | Year: {student.get('year', 'N/A')}")
    else:
        print(f"{student_id}: NOT FOUND")

print("\n" + "="*80)
print("✓ UPDATE COMPLETE")
print("="*80)
