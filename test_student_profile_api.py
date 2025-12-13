#!/usr/bin/env python3
"""Test student profile API endpoint"""

import sys
import requests
import json
sys.path.append('backend')

def test_student_profile_api():
    """Test the student profile API endpoint"""
    
    print("Testing Student Profile API Endpoint")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5000/api"
    
    # First, get a student user to test with
    try:
        from db.mysql import get_db
        db = get_db()
        
        # Get a student user
        student_user = db.execute_query("""
            SELECT u.*, s.student_id, s.year, s.section 
            FROM users u 
            JOIN students s ON u.id = s.user_id 
            WHERE u.role = 'student' 
            LIMIT 1
        """)
        
        if not student_user:
            print("❌ No student users found")
            return False
        
        student = student_user[0]
        print(f"🔍 Testing with student: {student['name']} (ID: {student['student_id']}, Year: {student['year']}, Section: {student['section']})")
        
        # Try to login as this student (we'll need to know their password or create a test token)
        # For now, let's test the profile logic directly by calling the function
        
        # Import the students blueprint function
        from blueprints.students import get_profile
        from flask import Flask
        from flask_jwt_extended import JWTManager, create_access_token
        
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        jwt = JWTManager(app)
        
        with app.app_context():
            # Create a test token for this user
            token = create_access_token(identity=student['id'])
            print(f"✅ Created test token for user ID: {student['id']}")
            
            # Test the profile endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.get(f"{base_url}/students/profile", headers=headers)
                print(f"📡 API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    profile_data = response.json()
                    print(f"✅ Profile loaded successfully!")
                    print(f"   Name: {profile_data.get('name')}")
                    print(f"   Student ID: {profile_data.get('student_id')}")
                    print(f"   Year: {profile_data.get('year')}")
                    print(f"   Section: {profile_data.get('section')}")
                    print(f"   Courses: {profile_data.get('courses', [])}")
                    print(f"   Instructors: {len(profile_data.get('instructors', []))} instructors")
                    
                    for instructor in profile_data.get('instructors', []):
                        print(f"      - {instructor.get('name')}: {instructor.get('course')}")
                    
                    return True
                else:
                    print(f"❌ API Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as api_error:
                print(f"❌ API request failed: {api_error}")
                return False
        
    except Exception as e:
        print(f"❌ Error testing student profile API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_student_profile_api()