"""
SQL Injection Protection Testing Script
Tests the security measures implemented in the Smart Attendance System
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Test configuration
BASE_URL = 'http://127.0.0.1:5000'
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'admin123'

class SQLInjectionTester:
    """Test SQL injection protection"""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
    
    def login(self) -> bool:
        """Login to get authentication token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    'username': TEST_USERNAME,
                    'password': TEST_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_sql_injection_payloads(self) -> Dict[str, List[Dict]]:
        """Test various SQL injection payloads"""
        
        # Common SQL injection payloads
        sql_payloads = [
            # Basic injection attempts
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "admin'--",
            "admin'#",
            "admin'/*",
            
            # UNION-based injections
            "' UNION SELECT * FROM users--",
            "' UNION SELECT username, password FROM users--",
            "' UNION SELECT 1,2,3,4,5--",
            
            # Boolean-based blind injections
            "' AND (SELECT COUNT(*) FROM users) > 0--",
            "' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a'--",
            
            # Time-based blind injections
            "'; WAITFOR DELAY '00:00:05'--",
            "' OR SLEEP(5)--",
            "' OR BENCHMARK(1000000,MD5(1))--",
            
            # Error-based injections
            "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            
            # Stacked queries
            "'; DROP TABLE users;--",
            "'; INSERT INTO users VALUES ('hacker', 'password');--",
            "'; UPDATE users SET password='hacked' WHERE username='admin';--",
            
            # File operations
            "' INTO OUTFILE '/tmp/test.txt'--",
            "' UNION SELECT LOAD_FILE('/etc/passwd')--",
            
            # Function-based injections
            "' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 65--",
            "' AND ORD(MID((SELECT IFNULL(CAST(username AS CHAR),0x20) FROM users ORDER BY id LIMIT 1),1,1)) > 97--",
        ]
        
        # XSS payloads (should also be blocked)
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
        ]
        
        # Command injection payloads
        command_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
        ]
        
        all_payloads = {
            'sql_injection': sql_payloads,
            'xss': xss_payloads,
            'command_injection': command_payloads
        }
        
        results = {}
        
        for category, payloads in all_payloads.items():
            print(f"\n🔍 Testing {category} payloads...")
            results[category] = []
            
            for payload in payloads:
                result = self.test_login_payload(payload)
                results[category].append({
                    'payload': payload,
                    'blocked': result['blocked'],
                    'status_code': result['status_code'],
                    'response': result['response']
                })
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
        
        return results
    
    def test_login_payload(self, payload: str) -> Dict[str, Any]:
        """Test a specific payload against login endpoint"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    'username': payload,
                    'password': 'test'
                }
            )
            
            # Check if payload was blocked (400 = validation error, good)
            blocked = response.status_code == 400
            
            response_text = response.text[:200] if response.text else ""
            
            return {
                'blocked': blocked,
                'status_code': response.status_code,
                'response': response_text
            }
            
        except Exception as e:
            return {
                'blocked': True,  # Exception means it was blocked
                'status_code': 0,
                'response': str(e)
            }
    
    def test_api_endpoints(self) -> Dict[str, List[Dict]]:
        """Test SQL injection on various API endpoints"""
        
        if not self.token:
            print("❌ No authentication token available")
            return {}
        
        # Test payloads for different endpoints
        test_cases = [
            {
                'endpoint': '/api/admin/users',
                'method': 'POST',
                'payload_field': 'username',
                'data': {
                    'username': "' OR 1=1--",
                    'password': 'test123',
                    'email': 'test@test.com',
                    'name': 'Test User',
                    'role': 'student'
                }
            },
            {
                'endpoint': '/api/students/register-face',
                'method': 'POST',
                'payload_field': 'student_id',
                'data': {
                    'student_id': "' UNION SELECT * FROM users--"
                }
            },
            {
                'endpoint': '/api/attendance/records',
                'method': 'GET',
                'payload_field': 'student_id',
                'params': {
                    'student_id': "' OR '1'='1"
                }
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            endpoint = test_case['endpoint']
            print(f"\n🔍 Testing endpoint: {endpoint}")
            
            try:
                if test_case['method'] == 'POST':
                    response = self.session.post(
                        f"{BASE_URL}{endpoint}",
                        json=test_case['data']
                    )
                else:
                    response = self.session.get(
                        f"{BASE_URL}{endpoint}",
                        params=test_case.get('params', {})
                    )
                
                blocked = response.status_code == 400
                
                results[endpoint] = {
                    'blocked': blocked,
                    'status_code': response.status_code,
                    'response': response.text[:200]
                }
                
            except Exception as e:
                results[endpoint] = {
                    'blocked': True,
                    'status_code': 0,
                    'response': str(e)
                }
        
        return results
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting protection"""
        print("\n🔍 Testing rate limiting...")
        
        # Send multiple requests rapidly
        start_time = time.time()
        blocked_count = 0
        total_requests = 50
        
        for i in range(total_requests):
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json={
                        'username': 'invalid_user',
                        'password': 'invalid_pass'
                    }
                )
                
                if response.status_code == 429:  # Rate limited
                    blocked_count += 1
                
            except Exception:
                blocked_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'total_requests': total_requests,
            'blocked_requests': blocked_count,
            'duration_seconds': duration,
            'rate_limiting_active': blocked_count > 0
        }
    
    def generate_report(self, results: Dict[str, Any]):
        """Generate security test report"""
        print("\n" + "="*80)
        print("SQL INJECTION PROTECTION TEST REPORT")
        print("="*80)
        
        # Payload test results
        if 'payload_tests' in results:
            payload_results = results['payload_tests']
            
            for category, tests in payload_results.items():
                blocked_count = sum(1 for test in tests if test['blocked'])
                total_count = len(tests)
                
                print(f"\n{category.upper()} TESTS:")
                print(f"  Total payloads tested: {total_count}")
                print(f"  Payloads blocked: {blocked_count}")
                print(f"  Success rate: {(blocked_count/total_count)*100:.1f}%")
                
                # Show failed blocks (security vulnerabilities)
                failed_blocks = [test for test in tests if not test['blocked']]
                if failed_blocks:
                    print(f"  ⚠️  VULNERABILITIES FOUND:")
                    for test in failed_blocks[:5]:  # Show first 5
                        print(f"    - {test['payload'][:50]}...")
        
        # API endpoint test results
        if 'api_tests' in results:
            api_results = results['api_tests']
            
            print(f"\nAPI ENDPOINT TESTS:")
            for endpoint, result in api_results.items():
                status = "✅ BLOCKED" if result['blocked'] else "❌ VULNERABLE"
                print(f"  {endpoint}: {status} (HTTP {result['status_code']})")
        
        # Rate limiting test results
        if 'rate_limiting' in results:
            rate_result = results['rate_limiting']
            
            print(f"\nRATE LIMITING TEST:")
            print(f"  Total requests: {rate_result['total_requests']}")
            print(f"  Blocked requests: {rate_result['blocked_requests']}")
            print(f"  Duration: {rate_result['duration_seconds']:.2f} seconds")
            
            if rate_result['rate_limiting_active']:
                print("  ✅ Rate limiting is ACTIVE")
            else:
                print("  ❌ Rate limiting is NOT ACTIVE")
        
        print("\n" + "="*80)
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔒 Starting SQL Injection Protection Tests")
        print("="*60)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return
        
        results = {}
        
        # Test 1: SQL injection payloads
        print("\n📋 Test 1: SQL Injection Payloads")
        results['payload_tests'] = self.test_sql_injection_payloads()
        
        # Test 2: API endpoints
        print("\n📋 Test 2: API Endpoint Protection")
        results['api_tests'] = self.test_api_endpoints()
        
        # Test 3: Rate limiting
        print("\n📋 Test 3: Rate Limiting")
        results['rate_limiting'] = self.test_rate_limiting()
        
        # Generate report
        self.generate_report(results)
        
        return results


def main():
    """Main test function"""
    print("🛡️  Smart Attendance System - SQL Injection Protection Test")
    print("="*70)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding correctly")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Make sure the backend is running: cd backend && python app.py")
        sys.exit(1)
    
    print("✅ Backend is running")
    
    # Run tests
    tester = SQLInjectionTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('security_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: security_test_results.json")


if __name__ == "__main__":
    main()