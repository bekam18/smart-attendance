"""
Test legitimate inputs to ensure they're not blocked
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_legitimate_inputs():
    """Test legitimate inputs that should NOT be blocked"""
    
    legitimate_inputs = [
        "admin",
        "user123",
        "john_doe",
        "student001",
        "instructor_smith",
        "test@example.com",
        "normalpassword123",
        "ValidUsername",
    ]
    
    print("✅ Testing Legitimate Inputs")
    print("="*40)
    
    allowed_count = 0
    total_count = len(legitimate_inputs)
    
    for i, input_val in enumerate(legitimate_inputs, 1):
        print(f"\n[{i}/{total_count}] Testing: {input_val}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    'username': input_val,
                    'password': 'testpass'
                },
                timeout=5
            )
            
            # We expect 401 (invalid credentials) not 400 (blocked input)
            if response.status_code == 401:
                print("  ✅ ALLOWED (401 - Invalid credentials, as expected)")
                allowed_count += 1
            elif response.status_code == 400:
                print("  ❌ BLOCKED (400 - Should not be blocked)")
                print(f"     Response: {response.text}")
            else:
                print(f"  ⚠️  UNEXPECTED STATUS: {response.status_code}")
                print(f"     Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ⚠️  ERROR: {e}")
    
    print("\n" + "="*40)
    print("RESULTS:")
    print(f"  Total inputs tested: {total_count}")
    print(f"  Legitimate inputs allowed: {allowed_count}")
    print(f"  Success rate: {(allowed_count/total_count)*100:.1f}%")
    
    if allowed_count == total_count:
        print("  🎉 ALL LEGITIMATE INPUTS ALLOWED!")
    else:
        print("  ⚠️  Some legitimate inputs were blocked")

if __name__ == "__main__":
    test_legitimate_inputs()