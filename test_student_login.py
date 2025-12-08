"""Test student login with provided credentials"""
import requests

BASE_URL = "http://127.0.0.1:5000"

students = [
    {"username": "STU001", "password": "Nabil123"},
    {"username": "STU002", "password": "Nardos123"}
]

print("="*80)
print("TESTING STUDENT LOGINS")
print("="*80)

for student in students:
    print(f"\n→ Testing {student['username']}...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": student['username'],
        "password": student['password']
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   Name: {data.get('user', {}).get('name')}")
        print(f"   Role: {data.get('user', {}).get('role')}")
        print(f"   Student ID: {data.get('user', {}).get('student_id')}")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
