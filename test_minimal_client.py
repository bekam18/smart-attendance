"""
Test client for minimal auth
"""

import requests

def test_minimal():
    try:
        response = requests.post(
            'http://127.0.0.1:5001/test',
            json={'username': 'admin', 'password': 'test'},
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_minimal()