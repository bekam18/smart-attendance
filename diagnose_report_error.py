"""
Diagnose report generation issues
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=== DIAGNOSING REPORT GENERATION ===\n")

# Step 1: Check if backend is running
print("1. Checking if backend is running...")
try:
    response = requests.get(f'{BASE_URL}/api/debug/health', timeout=5)
    print(f"   ✓ Backend is running (Status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Backend is NOT running: {e}")
    print("   Please start the backend first!")
    exit(1)

# Step 2: Login
print("\n2. Logging in as instructor 'be'...")
try:
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={'username': 'be', 'password': 'password'}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"   ✓ Login successful")
    else:
        print(f"   ✗ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Login error: {e}")
    exit(1)

# Step 3: Get instructor info
print("\n3. Getting instructor info...")
try:
    response = requests.get(
        f'{BASE_URL}/api/instructor/info',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code == 200:
        info = response.json()
        print(f"   ✓ Instructor: {info.get('username')}")
        print(f"   Courses: {info.get('courses')}")
        print(f"   Sections: {info.get('sections')}")
    else:
        print(f"   ✗ Failed to get info: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 4: Generate report
print("\n4. Generating report...")
report_data = {
    'report_type': 'daily',
    'section_id': 'A',
    'course_name': 'AI',
    'start_date': '2025-12-04',
    'end_date': '2025-12-04'
}

print(f"   Request data: {json.dumps(report_data, indent=2)}")

try:
    response = requests.post(
        f'{BASE_URL}/api/instructor/reports/generate',
        json=report_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"\n   Response Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n   ✓ Report generated successfully!")
        print(f"   Total Students: {result.get('total_students')}")
        print(f"   Total Sessions: {result.get('total_sessions')}")
    else:
        print(f"\n   ✗ Report generation failed!")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"\n   ✗ Request error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DIAGNOSIS COMPLETE ===")
