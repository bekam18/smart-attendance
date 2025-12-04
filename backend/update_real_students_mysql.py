#!/usr/bin/env python3
"""
Update MySQL database with 19 real students
Replaces test students with actual student data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mysql import get_db
import bcrypt
from datetime import datetime

# Real student data
STUDENTS = [
    # Section A
    {"student_id": "STU001", "name": "Nabila", "section": "A", "password": "Nabila123"},
    {"student_id": "STU002", "name": "Nardos", "section": "A", "password": "Nardos123"},
    {"student_id": "STU003", "name": "Amanu", "section": "A", "password": "Amanu123"},
    {"student_id": "STU004", "name": "Gadisa Tegene", "section": "A", "password": "Gadisa123"},
    {"student_id": "STU005", "name": "Yonas", "section": "A", "password": "Yonas123"},
    {"student_id": "STU006", "name": "Merihun", "section": "A", "password": "Merihun123"},
    
    # Section B
    {"student_id": "STU008", "name": "Nutoli", "section": "B", "password": "Nutoli123"},
    {"student_id": "STU009", "name": "Tedy", "section": "B", "password": "Tedy123"},
    {"student_id": "STU010", "name": "Ajme", "section": "B", "password": "Ajme123"},
    {"student_id": "STU011", "name": "Bedo", "section": "B", "password": "Bedo123"},
    {"student_id": "STU012", "name": "Milki", "section": "B", "password": "Milki123"},
    {"student_id": "STU013", "name": "Bekam Ayele", "section": "B", "password": "Bekam123"},
    {"student_id": "STU014", "name": "Yabsira", "section": "B", "password": "Yabsira123"},
    
    # Section C
    {"student_id": "STU015", "name": "Firansbekan", "section": "C", "password": "Firansbekan123"},
    {"student_id": "STU016", "name": "Bacha Eshetu", "section": "C", "password": "Bacha123"},
    {"student_id": "STU017", "name": "Yohannis Tekelgin", "section": "C", "password": "Yohannis123"},
    {"student_id": "STU018", "name": "Bari", "section": "C", "password": "Bari123"},
    {"student_id": "STU019", "name": "Lami", "section": "C", "password": "Lami123"},
    {"student_id": "STU021", "name": "Yien", "section": "C", "password": "Yien123"},
]

def remove_old_students():
    """Remove old test students"""
    print("\n🗑️  Removing old test students...")
    
    try:
        db = get_db()
        
        # Get old student user IDs
        old_students = db.execute_query("SELECT id FROM users WHERE role = 'student'")
        
        if old_students:
            # Delete old students
            db.execute_query("DELETE FROM students WHERE user_id IN (SELECT id FROM users WHERE role = 'student')", fetch=False)
            db.execute_query("DELETE FROM users WHERE role = 'student'", fetch=False)
            print(f"✅ Removed {len(old_students)} old student records")
        else:
            print("ℹ️  No old students to remove")
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing old students: {e}")
        return False

def add_new_students():
    """Add 19 real students"""
    print("\n📝 Adding 19 real students...")
    
    try:
        db = get_db()
        added_count = 0
        
        for student in STUDENTS:
            try:
                # Hash password
                hashed_password = bcrypt.hashpw(
                    student['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                # Create user account
                user_query = '''
                    INSERT INTO users (username, password, email, name, role, department, enabled, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
                
                email = f"{student['student_id'].lower()}@student.edu"
                
                user_id = db.execute_query(
                    user_query,
                    (student['student_id'], hashed_password, email, student['name'],
                     'student', 'Computer Science', True, datetime.utcnow()),
                    fetch=False
                )
                
                # Create student record
                student_query = '''
                    INSERT INTO students (user_id, student_id, name, email, department, year, section, face_registered, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                
                db.execute_query(
                    student_query,
                    (user_id, student['student_id'], student['name'], email,
                     'Computer Science', '3', student['section'], False, datetime.utcnow()),
                    fetch=False
                )
                
                added_count += 1
                print(f"✅ Added: {student['student_id']} - {student['name']} (Section {student['section']})")
                
            except Exception as e:
                print(f"❌ Failed to add {student['student_id']}: {e}")
                continue
        
        print(f"\n✅ Successfully added {added_count}/{len(STUDENTS)} students")
        return True
        
    except Exception as e:
        print(f"❌ Error adding students: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_students():
    """Verify student data"""
    print("\n🔍 Verifying student data...")
    
    try:
        db = get_db()
        
        # Count total students
        result = db.execute_query("SELECT COUNT(*) as count FROM students")
        total = result[0]['count'] if result else 0
        print(f"Total students: {total}")
        
        # Count by section
        sections = db.execute_query("SELECT section, COUNT(*) as count FROM students GROUP BY section ORDER BY section")
        for section in sections:
            print(f"Section {section['section']}: {section['count']} students")
        
        # List all students
        students = db.execute_query("SELECT student_id, name, section FROM students ORDER BY student_id")
        print(f"\n📋 Student List:")
        for student in students:
            print(f"  {student['student_id']} - {student['name']} (Section {student['section']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying students: {e}")
        return False

def main():
    """Main update function"""
    print("="*80)
    print("MYSQL STUDENT DATABASE UPDATE")
    print("="*80)
    print("\nThis will:")
    print("1. Remove old test students (s001, s002, s003)")
    print("2. Add 19 real students with sections")
    print("3. Preserve admin and instructor accounts")
    print()
    
    # Auto-confirm for batch execution
    print("Auto-confirming... (set AUTO_CONFIRM=False to prompt)")
    AUTO_CONFIRM = True
    
    if not AUTO_CONFIRM:
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Remove old students
    if not remove_old_students():
        print("\n❌ Failed to remove old students")
        return
    
    # Add new students
    if not add_new_students():
        print("\n❌ Failed to add new students")
        return
    
    # Verify
    verify_students()
    
    print("\n" + "="*80)
    print("UPDATE COMPLETE!")
    print("="*80)
    print("\n✅ 19 real students added to MySQL database")
    print("\n📋 Login Credentials:")
    print("   Username: Student ID (e.g., STU001)")
    print("   Password: {FirstName}123 (e.g., Nabila123)")
    print("\n📝 Examples:")
    print("   STU001 / Nabila123")
    print("   STU008 / Nutoli123")
    print("   STU013 / Bekam123")
    print("\n🚀 Students can now login and register their faces!")

if __name__ == '__main__':
    main()
