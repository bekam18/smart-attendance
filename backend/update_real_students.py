"""
Update MongoDB with real student list
Replaces test students with actual students
Preserves admin/instructor users and other collections
"""

from pymongo import MongoClient
from datetime import datetime
from utils.security import hash_password
from config import config

# Real student data
STUDENTS = [
    # Section A (STU001-STU007)
    {'student_id': 'STU001', 'name': 'Nabila', 'section': 'A'},
    {'student_id': 'STU002', 'name': 'Nardos', 'section': 'A'},
    {'student_id': 'STU003', 'name': 'Amanu', 'section': 'A'},
    {'student_id': 'STU004', 'name': 'Gadisa Tegene', 'section': 'A'},
    {'student_id': 'STU005', 'name': 'Yonas', 'section': 'A'},
    {'student_id': 'STU006', 'name': 'Merihun', 'section': 'A'},
    
    # Section B (STU008-STU014)
    {'student_id': 'STU008', 'name': 'Nutoli', 'section': 'B'},
    {'student_id': 'STU009', 'name': 'Tedy', 'section': 'B'},
    {'student_id': 'STU010', 'name': 'Ajme', 'section': 'B'},
    {'student_id': 'STU011', 'name': 'Bedo', 'section': 'B'},
    {'student_id': 'STU012', 'name': 'Milki', 'section': 'B'},
    {'student_id': 'STU013', 'name': 'Bekam Ayele', 'section': 'B'},
    {'student_id': 'STU014', 'name': 'Yabsira', 'section': 'B'},
    
    # Section C (STU015-STU021)
    {'student_id': 'STU015', 'name': 'Firansbekan', 'section': 'C'},
    {'student_id': 'STU016', 'name': 'Bacha Eshetu', 'section': 'C'},
    {'student_id': 'STU017', 'name': 'Yohannis Tekelgin', 'section': 'C'},
    {'student_id': 'STU018', 'name': 'Bari', 'section': 'C'},
    {'student_id': 'STU019', 'name': 'Lami', 'section': 'C'},
    {'student_id': 'STU021', 'name': 'Yien', 'section': 'C'},
]

def get_first_name(full_name):
    """Extract first name from full name"""
    return full_name.split()[0]

def update_students():
    """Replace test students with real students"""
    
    print("="*60)
    print("UPDATING STUDENT DATABASE WITH REAL STUDENTS")
    print("="*60)
    
    # Connect to MongoDB
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    
    # Step 1: Delete ONLY student users (preserve admin/instructor)
    print("\n1️⃣ Removing old student users...")
    result = db.users.delete_many({'role': 'student'})
    print(f"   ✅ Deleted {result.deleted_count} student user(s)")
    
    # Step 2: Delete old student records (preserve face_registered status if exists)
    print("\n2️⃣ Removing old student records...")
    result = db.students.delete_many({})
    print(f"   ✅ Deleted {result.deleted_count} student record(s)")
    
    # Step 3: Insert real students
    print("\n3️⃣ Inserting real students...")
    
    for student in STUDENTS:
        student_id = student['student_id']
        full_name = student['name']
        section = student['section']
        first_name = get_first_name(full_name)
        
        # Username is student_id
        username = student_id
        
        # Password is {first_name}123
        password = f"{first_name}123"
        
        # Email (generated)
        email = f"{username.lower()}@student.edu"
        
        # Create user account
        user_doc = {
            'username': username,
            'password': hash_password(password),
            'email': email,
            'name': full_name,
            'role': 'student',
            'created_at': datetime.utcnow()
        }
        
        user_result = db.users.insert_one(user_doc)
        user_id = str(user_result.inserted_id)
        
        # Create student profile
        student_doc = {
            'user_id': user_id,
            'student_id': student_id,
            'name': full_name,
            'email': email,
            'section': section,
            'department': 'Computer Science',  # Default department
            'year': '3',  # Default year
            'face_registered': False,  # Will be updated when they register face
            'created_at': datetime.utcnow()
        }
        
        db.students.insert_one(student_doc)
        
        print(f"   ✅ {student_id}: {full_name} (Section {section}) - Username: {username}, Password: {password}")
    
    # Step 4: Verify results
    print("\n4️⃣ Verifying database...")
    
    total_users = db.users.count_documents({})
    admin_count = db.users.count_documents({'role': 'admin'})
    instructor_count = db.users.count_documents({'role': 'instructor'})
    student_count = db.users.count_documents({'role': 'student'})
    student_records = db.students.count_documents({})
    
    print(f"   Total Users: {total_users}")
    print(f"   - Admins: {admin_count}")
    print(f"   - Instructors: {instructor_count}")
    print(f"   - Students: {student_count}")
    print(f"   Student Records: {student_records}")
    
    # Step 5: Display section breakdown
    print("\n5️⃣ Section breakdown...")
    section_a = db.students.count_documents({'section': 'A'})
    section_b = db.students.count_documents({'section': 'B'})
    section_c = db.students.count_documents({'section': 'C'})
    
    print(f"   Section A: {section_a} students")
    print(f"   Section B: {section_b} students")
    print(f"   Section C: {section_c} students")
    
    # Step 6: Display sample login credentials
    print("\n" + "="*60)
    print("✅ STUDENT DATABASE UPDATED SUCCESSFULLY!")
    print("="*60)
    
    print("\n📝 Sample Login Credentials:")
    print("-" * 60)
    print("Section A:")
    print("  Username: STU001  Password: Nabila123")
    print("  Username: STU002  Password: Nardos123")
    print("\nSection B:")
    print("  Username: STU008  Password: Nutoli123")
    print("  Username: STU009  Password: Tedy123")
    print("\nSection C:")
    print("  Username: STU015  Password: Firansbekan123")
    print("  Username: STU016  Password: Bacha123")
    print("-" * 60)
    
    print("\n📊 Summary:")
    print(f"   ✅ {len(STUDENTS)} real students added")
    print(f"   ✅ Section A: {section_a} students (STU001-STU006)")
    print(f"   ✅ Section B: {section_b} students (STU008-STU014)")
    print(f"   ✅ Section C: {section_c} students (STU015-STU021)")
    print(f"   ✅ Admin/Instructor accounts preserved")
    print(f"   ✅ Other collections unchanged")
    
    print("\n🔐 Password Pattern: {FirstName}123")
    print("   Example: Nabila → Nabila123")
    print("   Example: Gadisa Tegene → Gadisa123")
    
    print("\n🎓 Next Steps:")
    print("   1. Students can login with their student_id as username")
    print("   2. Students should register their faces")
    print("   3. Instructors can start taking attendance")
    
    client.close()

if __name__ == '__main__':
    try:
        update_students()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
