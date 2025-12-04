"""Test the sections-by-course endpoint"""
import requests
import json

# Login first
print("=" * 60)
print("TESTING SECTIONS-BY-COURSE ENDPOINT")
print("=" * 60)

# Login
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "username": "instructor@example.com",
    "password": "password123"
}

print("\n1. Logging in...")
response = requests.post(login_url, json=login_data)
if response.status_code == 200:
    token = response.json()['token']
    print(f"✓ Login successful")
    print(f"Token: {token[:50]}...")
else:
    print(f"✗ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

# Get instructor info
print("\n2. Getting instructor info...")
info_url = "http://localhost:5000/api/instructor/info"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(info_url, headers=headers)
if response.status_code == 200:
    info = response.json()
    print(f"✓ Instructor: {info['name']}")
    print(f"  Courses: {info.get('courses', [])}")
    print(f"  Sections: {info.get('sections', [])}")
    courses = info.get('courses', [])
else:
    print(f"✗ Failed to get info: {response.status_code}")
    print(response.text)
    exit(1)

# Test sections-by-course for each course
print("\n3. Testing sections-by-course endpoint...")
for course in courses:
    print(f"\n   Course: {course}")
    sections_url = f"http://localhost:5000/api/instructor/sections-by-course?course_name={course}"
    response = requests.get(sections_url, headers=headers)
    
    if response.status_code == 200:
        sections = response.json()['sections']
        print(f"   ✓ Sections: {sections}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
        print(f"   {response.text}")

print("\n" + "=" * 60)
