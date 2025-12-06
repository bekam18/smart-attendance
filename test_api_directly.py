import requests
import json

# Login first to get token
login_url = 'http://127.0.0.1:5000/api/auth/login'
login_data = {
    'username': 'beki',
    'password': 'beki123'
}

print("="*60)
print("TESTING REPORT API DIRECTLY")
print("="*60)

try:
    # Login
    print("\n1. Logging in...")
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        exit(1)
    
    token = login_response.json()['access_token']
    print(f"✅ Login successful, got token")
    
    # Generate report
    print("\n2. Generating report...")
    report_url = 'http://127.0.0.1:5000/api/instructor/reports/generate'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    report_data = {
        'report_type': 'daily',
        'section_id': 'A',
        'course_name': 'Java',
        'start_date': '2025-12-01',
        'end_date': '2025-12-31'
    }
    
    print(f"Request data: {json.dumps(report_data, indent=2)}")
    
    report_response = requests.post(report_url, json=report_data, headers=headers)
    
    if report_response.status_code != 200:
        print(f"❌ Report generation failed: {report_response.status_code}")
        print(f"Response: {report_response.text}")
        exit(1)
    
    result = report_response.json()
    
    print(f"\n✅ Report generated successfully!")
    print(f"\n3. Report Summary:")
    print(f"   Total Sessions: {result['total_sessions']}")
    print(f"   Total Students: {result['total_students']}")
    print(f"   Section: {result['section_id']}")
    print(f"   Course: {result['course_name']}")
    
    print(f"\n4. Student Data (first 5):")
    for i, student in enumerate(result['data'][:5]):
        print(f"\n   [{i+1}] {student['student_id']} - {student['name']}")
        print(f"       Present: {student['present_count']}")
        print(f"       Absent: {student['absent_count']}")
        print(f"       Total Sessions: {student['total_sessions']}")
        print(f"       Percentage: {student['percentage']:.1f}%")
    
    # Find students with present > 0
    print(f"\n5. Students with attendance:")
    present_students = [s for s in result['data'] if s['present_count'] > 0]
    if present_students:
        for student in present_students:
            print(f"   ✅ {student['student_id']} ({student['name']}): {student['present_count']} present")
    else:
        print(f"   ❌ NO STUDENTS WITH PRESENT COUNT > 0!")
        print(f"   This is the bug - checking all students:")
        for student in result['data']:
            print(f"      {student['student_id']}: present={student['present_count']}, absent={student['absent_count']}")
    
    print("\n" + "="*60)
    
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Make sure it's running on http://127.0.0.1:5000")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
