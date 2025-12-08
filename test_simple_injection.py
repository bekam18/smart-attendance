"""
Simple test to isolate the regex issue
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_simple_login():
    """Test a simple legitimate login"""
    
    print("🔍 Testing simple legitimate login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                'username': 'admin',
                'password': 'admin123'
            },
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Expected 401 - Invalid credentials (normal behavior)")
        elif response.status_code == 400:
            print("❌ 400 - Input blocked by security middleware")
        elif response.status_code == 500:
            print("❌ 500 - Internal server error")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  ERROR: {e}")

if __name__ == "__main__":
    test_simple_login()