"""
Direct SQL Injection Test - Tests the core protection without complex middleware
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_sql_injections():
    """Test various SQL injection payloads"""
    
    payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' OR 1=1#",
        "admin'--",
        "' UNION SELECT * FROM users--",
        "'; DROP TABLE users;--",
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
    ]
    
    print("🔒 Testing SQL Injection Protection")
    print("="*50)
    
    blocked_count = 0
    total_count = len(payloads)
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n[{i}/{total_count}] Testing: {payload[:30]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    'username': payload,
                    'password': 'test'
                },
                timeout=5
            )
            
            if response.status_code == 400:
                print("  ✅ BLOCKED")
                blocked_count += 1
            else:
                print(f"  ❌ NOT BLOCKED (Status: {response.status_code})")
                print(f"     Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ⚠️  ERROR: {e}")
    
    print("\n" + "="*50)
    print("RESULTS:")
    print(f"  Total payloads tested: {total_count}")
    print(f"  Payloads blocked: {blocked_count}")
    print(f"  Success rate: {(blocked_count/total_count)*100:.1f}%")
    
    if blocked_count == total_count:
        print("  🎉 ALL PAYLOADS BLOCKED - PROTECTION IS WORKING!")
    elif blocked_count > 0:
        print("  ⚠️  PARTIAL PROTECTION - Some payloads blocked")
    else:
        print("  ❌ NO PROTECTION - All payloads passed through")

if __name__ == "__main__":
    test_sql_injections()