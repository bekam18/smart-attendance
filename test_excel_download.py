import requests
import json

# Login
login_url = 'http://127.0.0.1:5000/api/auth/login'
login_data = {
    'username': 'beki',
    'password': 'beki123'
}

print("="*60)
print("TESTING EXCEL DOWNLOAD")
print("="*60)

try:
    # Login
    print("\n1. Logging in...")
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        exit(1)
    
    token = login_response.json()['access_token']
    print(f"✅ Login successful")
    
    # Download Excel
    print("\n2. Downloading Excel...")
    excel_url = 'http://127.0.0.1:5000/api/instructor/reports/download/excel'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    excel_data = {
        'report_type': 'daily',
        'section_id': 'A',
        'course_name': 'Java',
        'start_date': '2025-12-01',
        'end_date': '2025-12-31'
    }
    
    print(f"Request data: {json.dumps(excel_data, indent=2)}")
    
    excel_response = requests.post(excel_url, json=excel_data, headers=headers)
    
    if excel_response.status_code != 200:
        print(f"\n❌ Excel download failed: {excel_response.status_code}")
        print(f"Response: {excel_response.text}")
        exit(1)
    
    # Save the file
    with open('test_report.xlsx', 'wb') as f:
        f.write(excel_response.content)
    
    print(f"\n✅ Excel downloaded successfully!")
    print(f"   File saved as: test_report.xlsx")
    print(f"   File size: {len(excel_response.content)} bytes")
    
    print("\n" + "="*60)
    
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Make sure it's running on http://127.0.0.1:5000")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
