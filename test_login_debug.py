import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_login():
    """Test normal login"""
    
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
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()