"""
Test student profile API to check courses
"""

import requests
import json

API_URL = 'http://127.0.0.1:5000'

# First, login as a student
print("=" * 60)
print("TESTING STUDENT PROFILE API")
print("=" * 60)

# Login
print("\n1. Logging in as student...")
login_response = requests.post(
    f"{API_URL}/api/auth/login",
    json={
        'username': 'STU002',
        'password': 'student123'
    }
)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print("✅ Login successful")
    
    # Get profile
    print("\n2. Fetching student profile...")
    profile_response = requests.get(
        f"{API_URL}/api/students/profile",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print("✅ Profile fetched successfully")
        print(f"\nStudent: {profile['name']} ({profile['student_id']})")
        print(f"Year: {profile['year']}, Section: {profile['section']}")
        print(f"\nCourses ({len(profile.get('courses', []))}): ")
        for course in profile.get('courses', []):
            print(f"  - {course}")
        print(f"\nInstructors ({len(profile.get('instructors', []))}): ")
        for instructor in profile.get('instructors', []):
            print(f"  - {instructor['name']}: {instructor['course']}")
    else:
        print(f"❌ Failed to fetch profile: {profile_response.status_code}")
        print(profile_response.text)
    
    # Get attendance
    print("\n3. Fetching attendance history...")
    attendance_response = requests.get(
        f"{API_URL}/api/students/attendance",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if attendance_response.status_code == 200:
        attendance = attendance_response.json()
        print(f"✅ Found {len(attendance)} attendance records")
        
        if len(attendance) > 0:
            print("\nSample records:")
            for record in attendance[:3]:
                instructor = record.get('instructor_name', 'N/A')
                print(f"  - {record['date']}: {record['course_name']} - {instructor} ({record['status']})")
    else:
        print(f"❌ Failed to fetch attendance: {attendance_response.status_code}")
        print(attendance_response.text)
        
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)

print("\n" + "=" * 60)
