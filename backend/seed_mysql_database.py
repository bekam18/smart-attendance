#!/usr/bin/env python3
"""
Seed MySQL database with initial data
Use this if you don't have MongoDB data to migrate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mysql import get_db
import bcrypt
from datetime import datetime

def create_admin_user():
    """Create default admin user"""
    print("\n📋 Creating admin user...")
    
    try:
        db = get_db()
        
        # Hash password
        password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query = '''
            INSERT INTO users 
            (username, password, email, name, role, enabled, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        
        params = (
            'admin',
            password,
            'admin@smartattendance.com',
            'System Administrator',
            'admin',
            True,
            datetime.utcnow()
        )
        
        db.execute_query(query, params, fetch=False)
        print("✅ Admin user created")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@smartattendance.com")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def create_sample_instructor():
    """Create sample instructor user"""
    print("\n📋 Creating sample instructor...")
    
    try:
        db = get_db()
        
        # Hash password
        password = bcrypt.hashpw('instructor123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query = '''
            INSERT INTO users 
            (username, password, email, name, role, department, course_name, 
             class_year, session_types, sections, enabled, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        import json
        params = (
            'instructor1',
            password,
            'instructor@smartattendance.com',
            'Dr. John Smith',
            'instructor',
            'Computer Science',
            'Data Structures',
            '2024',
            json.dumps(['lab', 'theory']),
            json.dumps(['A', 'B']),
            True,
            datetime.utcnow()
        )
        
        db.execute_query(query, params, fetch=False)
        print("✅ Instructor user created")
        print("   Username: instructor1")
        print("   Password: instructor123")
        print("   Email: instructor@smartattendance.com")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create instructor: {e}")
        return False

def create_sample_students():
    """Create sample students"""
    print("\n📋 Creating sample students...")
    
    try:
        db = get_db()
        
        students = [
            ('S001', 'Alice Johnson', 'alice@student.com', 'Computer Science', '2024', 'A'),
            ('S002', 'Bob Smith', 'bob@student.com', 'Computer Science', '2024', 'A'),
            ('S003', 'Charlie Brown', 'charlie@student.com', 'Computer Science', '2024', 'B'),
        ]
        
        for student_id, name, email, dept, year, section in students:
            # Create user account
            password = bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user_query = '''
                INSERT INTO users 
                (username, password, email, name, role, department, enabled, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            user_params = (
                student_id.lower(),
                password,
                email,
                name,
                'student',
                dept,
                True,
                datetime.utcnow()
            )
            
            user_id = db.execute_query(user_query, user_params, fetch=False)
            
            # Create student record
            student_query = '''
                INSERT INTO students 
                (user_id, student_id, name, email, department, year, section, 
                 face_registered, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            student_params = (
                user_id,
                student_id,
                name,
                email,
                dept,
                year,
                section,
                False,
                datetime.utcnow()
            )
            
            db.execute_query(student_query, student_params, fetch=False)
            print(f"✅ Created student: {student_id} - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create students: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main seeding function"""
    print("="*80)
    print("MYSQL DATABASE SEEDING")
    print("="*80)
    print("\nThis will create initial users and data in MySQL")
    print("Use this if you don't have MongoDB data to migrate")
    print()
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    success_count = 0
    total = 3
    
    if create_admin_user():
        success_count += 1
    
    if create_sample_instructor():
        success_count += 1
    
    if create_sample_students():
        success_count += 1
    
    print("\n" + "="*80)
    print("SEEDING SUMMARY")
    print("="*80)
    print(f"Completed: {success_count}/{total} tasks")
    
    if success_count == total:
        print("\n🎉 Database seeded successfully!")
        print("\n📋 You can now login with:")
        print("   Admin:")
        print("     Username: admin")
        print("     Password: admin123")
        print()
        print("   Instructor:")
        print("     Username: instructor1")
        print("     Password: instructor123")
        print()
        print("   Students:")
        print("     Username: s001, s002, s003")
        print("     Password: student123")
        print()
        print("Next step: Start the backend with 'python app.py'")
    else:
        print(f"\n⚠️  {total - success_count} tasks failed")

if __name__ == '__main__':
    main()
