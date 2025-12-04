"""
Database seeding script for SmartAttendance
Creates demo users for testing
"""

from datetime import datetime
from utils.security import hash_password
from config import config
from db.mysql import get_db
import json

def seed_database():
    """Seed the database with demo users"""
    
    print("🌱 Seeding database...")
    
    # Connect to MySQL
    db = get_db()
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing data...")
    db.execute_query("DELETE FROM attendance", fetch=False)
    db.execute_query("DELETE FROM sessions", fetch=False)
    db.execute_query("DELETE FROM students", fetch=False)
    db.execute_query("DELETE FROM users", fetch=False)
    
    # Create Admin User
    print("Creating admin user...")
    admin_query = """
        INSERT INTO users (username, password, email, name, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    admin_values = (
        'admin',
        hash_password('admin123'),
        'admin@smartattendance.com',
        'System Administrator',
        'admin',
        datetime.utcnow()
    )
    db.execute_query(admin_query, admin_values, fetch=False)
    print(f"✅ Admin created: admin / admin123")
    
    # Create Instructor Users
    print("Creating instructor users...")
    instructors = [
        {
            'username': 'instructor',
            'password': hash_password('inst123'),
            'email': 'instructor@smartattendance.com',
            'name': 'Dr. John Smith',
            'role': 'instructor',
            'department': 'Computer Science',
            'course_name': 'Computer Science',
            'class_year': '2nd Year',
            'session_types': ['lab', 'theory'],
            'sections': ['A', 'B']
        },
        {
            'username': 'instructor2',
            'password': hash_password('inst123'),
            'email': 'instructor2@smartattendance.com',
            'name': 'Prof. Jane Doe',
            'role': 'instructor',
            'department': 'Mathematics',
            'course_name': 'Mathematics',
            'class_year': '3rd Year',
            'session_types': ['theory'],
            'sections': ['A', 'C']
        }
    ]
    
    instructor_query = """
        INSERT INTO users (username, password, email, name, role, department, course_name, class_year, session_types, sections, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for instructor in instructors:
        instructor_values = (
            instructor['username'],
            instructor['password'],
            instructor['email'],
            instructor['name'],
            instructor['role'],
            instructor['department'],
            instructor['course_name'],
            instructor['class_year'],
            json.dumps(instructor['session_types']),
            json.dumps(instructor['sections']),
            datetime.utcnow()
        )
        db.execute_query(instructor_query, instructor_values, fetch=False)
        print(f"✅ Instructor created: {instructor['username']} / inst123 (Sections: {', '.join(instructor['sections'])})")
    
    # Create Student Users
    print("Creating student users...")
    students_data = [
        {
            'username': 'student',
            'password': hash_password('stud123'),
            'email': 'student@smartattendance.com',
            'name': 'Alice Johnson',
            'student_id': 'STU001',
            'department': 'Computer Science',
            'year': '3'
        },
        {
            'username': 'student2',
            'password': hash_password('stud123'),
            'email': 'student2@smartattendance.com',
            'name': 'Bob Williams',
            'student_id': 'STU002',
            'department': 'Computer Science',
            'year': '2'
        },
        {
            'username': 'student3',
            'password': hash_password('stud123'),
            'email': 'student3@smartattendance.com',
            'name': 'Charlie Brown',
            'student_id': 'STU003',
            'department': 'Mathematics',
            'year': '4'
        },
        {
            'username': 'student4',
            'password': hash_password('stud123'),
            'email': 'student4@smartattendance.com',
            'name': 'Diana Prince',
            'student_id': 'STU004',
            'department': 'Computer Science',
            'year': '1'
        },
        {
            'username': 'student5',
            'password': hash_password('stud123'),
            'email': 'student5@smartattendance.com',
            'name': 'Ethan Hunt',
            'student_id': 'STU005',
            'department': 'Engineering',
            'year': '3'
        }
    ]
    
    user_query = """
        INSERT INTO users (username, password, email, name, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    student_query = """
        INSERT INTO students (user_id, student_id, name, email, department, year, face_registered, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for student_data in students_data:
        # Create user
        user_values = (
            student_data['username'],
            student_data['password'],
            student_data['email'],
            student_data['name'],
            'student',
            datetime.utcnow()
        )
        user_id = db.execute_query(user_query, user_values, fetch=False)
        
        # Create student profile
        student_values = (
            user_id,
            student_data['student_id'],
            student_data['name'],
            student_data['email'],
            student_data['department'],
            student_data['year'],
            False,
            datetime.utcnow()
        )
        db.execute_query(student_query, student_values, fetch=False)
        
        print(f"✅ Student created: {student_data['username']} / stud123 ({student_data['student_id']})")
    
    print("\n✅ Database seeding completed!")
    print("\n📝 Demo Credentials:")
    print("=" * 50)
    print("Admin:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nInstructor:")
    print("  Username: instructor")
    print("  Password: inst123")
    print("\nStudent:")
    print("  Username: student")
    print("  Password: stud123")
    print("=" * 50)
    
    # Print statistics
    print("\n📊 Database Statistics:")
    total_users = db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
    total_admins = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")[0]['count']
    total_instructors = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'instructor'")[0]['count']
    total_students = db.execute_query("SELECT COUNT(*) as count FROM students")[0]['count']
    
    print(f"  Total Users: {total_users}")
    print(f"  Admins: {total_admins}")
    print(f"  Instructors: {total_instructors}")
    print(f"  Students: {total_students}")

if __name__ == '__main__':
    seed_database()
