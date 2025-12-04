"""
COMPLETE DATA RESTORATION SCRIPT
Restores all students, instructors, and admin with correct structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db.mongo import init_db
from utils.security import hash_password
from datetime import datetime

print("="*80)
print("COMPLETE DATA RESTORATION")
print("="*80)

# Initialize database
print("\nConnecting to MongoDB...")
db = init_db()

if db is None:
    print("❌ Failed to connect to MongoDB")
    sys.exit(1)

print("✅ Connected to database")

# Check current state
print("\n📊 Current Database State:")
print(f"  Users: {db.execute_query('SELECT COUNT(*) as count FROM users')[0]['count']}")
print(f"  Students: {db.execute_query('SELECT COUNT(*) as count FROM students')[0]['count']}")
print(f"  Attendance: {db.execute_query('SELECT COUNT(*) as count FROM attendance')[0]['count']}")
print(f"  Sessions: {db.execute_query('SELECT COUNT(*) as count FROM sessions')[0]['count']}")

# Ask for confirmation
print("\n⚠️  This will restore all data. Existing data will be preserved unless duplicates exist.")
response = input("Continue? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    sys.exit(0)

print("\n" + "="*80)
print("RESTORING DATA")
print("="*80)

# 1. CREATE ADMIN
print("\n1️⃣  Creating Admin...")
admin_exists = db.execute_query('SELECT * FROM users WHERE username = "admin"')
if not admin_exists:
    admin_user = {
        'username': 'admin',
        'password': hash_password('admin123'),
        'email': 'admin@smartattendance.com',
        'name': 'System Administrator',
        'role': 'admin',
        'enabled': True,
        'created_at': datetime.utcnow()
    }
    db.execute_query('INSERT INTO users (username, password, email, name, role, created_at) VALUES (%s, %s, %s, %s, %s, %s)', (admin_user['username'], admin_user['password'], admin_user['email'], admin_user['name'], admin_user['role'], admin_user['created_at']), fetch=False)
    print("✅ Admin created: admin / admin123")
else:
    print("✅ Admin already exists")

# 2. CREATE INSTRUCTORS
print("\n2️⃣  Creating Instructors...")
instructors_data = [
    {
        'username': 'instructor',
        'password': 'inst123',
        'email': 'instructor@smartattendance.com',
        'name': 'Dr. John Smith',
        'department': 'Computer Science',
        'courses': ['CS101', 'CS201'],
        'sections': ['A', 'B']
    },
    {
        'username': 'instructor2',
        'password': 'inst123',
        'email': 'instructor2@smartattendance.com',
        'name': 'Prof. Jane Doe',
        'department': 'Mathematics',
        'courses': ['MATH101'],
        'sections': ['A']
    }
]

for inst_data in instructors_data: