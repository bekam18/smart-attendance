"""
Quick script to check database status and users
"""
from db.mongo import get_db

def check_database():
    print("🔍 Checking database status...")
    
    try:
        db = get_db()
        
        # Count users
        user_count = db.users.count_documents({})
        print(f"\n📊 Total users in database: {user_count}")
        
        if user_count == 0:
            print("\n❌ No users found in database!")
            print("💡 Solution: Run 'python seed_db.py' to create demo users")
            return
        
        # List all users
        print("\n👥 Users in database:")
        users = db.users.find({}, {'username': 1, 'role': 1, 'email': 1})
        for user in users:
            print(f"  - Username: {user['username']}, Role: {user['role']}, Email: {user.get('email', 'N/A')}")
        
        print("\n✅ Database is properly configured!")
        print("\n🔑 Demo credentials:")
        print("  Admin: admin / admin123")
        print("  Instructor: instructor / inst123")
        print("  Student: student / stud123")
        
    except Exception as e:
        print(f"\n❌ Error connecting to database: {e}")
        print("💡 Check your MONGODB_URI in backend/.env")

if __name__ == '__main__':
    check_database()
