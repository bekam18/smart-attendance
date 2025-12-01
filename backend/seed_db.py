"""
Database seeding script for SmartAttendance
Creates demo users for testing
"""

from pymongo import MongoClient
from datetime import datetime
from utils.security import hash_password
from config import config

def seed_database():
    """Seed the database with demo users"""
    
    print("🌱 Seeding database...")
    
    # Connect to MongoDB
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing data...")
    db.users.delete_many({})
    db.students.delete_many({})
    db.attendance.delete_many({})
    db.sessions.delete_many({})
    
    # Create Admin User
    print("Creating admin user...")
    admin_user = {
        'username': 'admin',
        'password': hash_password('admin123'),
        'email': 'admin@smartattendance.com',
        'name': 'System Administrator',
        'role': 'admin',
        'created_at': datetime.utcnow()
    }
    admin_result = db.users.insert_one(admin_user)
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
            'sections': ['CS101-A', 'CS201-B'],  # Sections this instructor teaches
            'created_at': datetime.utcnow()
        },
        {
            'username': 'instructor2',
            'password': hash_password('inst123'),
            'email': 'instructor2@smartattendance.com',
            'name': 'Prof. Jane Doe',
            'role': 'instructor',
            'department': 'Mathematics',
            'sections': ['MATH101-A', 'MATH201-C'],  # Different sections
            'created_at': datetime.utcnow()
        }
    ]
    
    for instructor in instructors:
        db.users.insert_one(instructor)
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
    
    for student_data in students_data:
        # Create user
        user_doc = {
            'username': student_data['username'],
            'password': student_data['password'],
            'email': student_data['email'],
            'name': student_data['name'],
            'role': 'student',
            'created_at': datetime.utcnow()
        }
        user_result = db.users.insert_one(user_doc)
        user_id = str(user_result.inserted_id)
        
        # Create student profile
        student_doc = {
            'user_id': user_id,
            'student_id': student_data['student_id'],
            'name': student_data['name'],
            'email': student_data['email'],
            'department': student_data['department'],
            'year': student_data['year'],
            'face_registered': False,
            'created_at': datetime.utcnow()
        }
        db.students.insert_one(student_doc)
        
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
    print(f"  Total Users: {db.users.count_documents({})}")
    print(f"  Admins: {db.users.count_documents({'role': 'admin'})}")
    print(f"  Instructors: {db.users.count_documents({'role': 'instructor'})}")
    print(f"  Students: {db.students.count_documents({})}")
    
    client.close()

if __name__ == '__main__':
    seed_database()
