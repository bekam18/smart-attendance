"""
Test script for session management features:
1. Stop Camera (daily end)
2. End Session (semester end)
3. Reopen Session (after 12 hours)
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# Test credentials (instructor)
USERNAME = "bekam"
PASSWORD = "instructor123"  # Update with actual password

def login():
    """Login and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ Logged in successfully")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def get_sessions(token):
    """Get all sessions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/attendance/sessions", headers=headers)
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"\n📋 Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"\n  ID: {session['id']}")
            print(f"  Name: {session['name']}")
            print(f"  Status: {session['status']}")
            print(f"  Can Reopen: {session.get('can_reopen', False)}")
            if session.get('hours_until_reopen'):
                print(f"  Hours Until Reopen: {session['hours_until_reopen']:.1f}")
        return sessions
    else:
        print(f"❌ Failed to get sessions: {response.text}")
        return []

def start_test_session(token):
    """Start a test session"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Session - Session Management",
        "course": "Test Course",
        "section_id": "A",
        "year": "4th Year",
        "session_type": "lab",
        "time_block": "morning"
    }
    
    response = requests.post(f"{BASE_URL}/api/attendance/start-session", 
                            headers=headers, json=data)
    
    if response.status_code == 201:
        session_id = response.json()['session_id']
        print(f"\n✅ Test session created: {session_id}")
        return session_id
    else:
        print(f"❌ Failed to create session: {response.text}")
        return None

def stop_camera(token, session_id):
    """Stop camera (daily end) - marks absent students"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/attendance/mark-absent",
                            headers=headers, json={"session_id": session_id})
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Camera stopped successfully")
        print(f"  Absent Count: {data.get('absent_count', 0)}")
        print(f"  Total Students: {data.get('total_students', 0)}")
        print(f"  Present Count: {data.get('present_count', 0)}")
        return True
    else:
        print(f"❌ Failed to stop camera: {response.text}")
        return False

def end_session_permanent(token, session_id):
    """End session permanently (semester end)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/attendance/end-session",
                            headers=headers, 
                            json={"session_id": session_id, "end_type": "semester"})
    
    if response.status_code == 200:
        print(f"\n✅ Session ended permanently")
        return True
    else:
        print(f"❌ Failed to end session: {response.text}")
        return False

def reopen_session(token, session_id):
    """Reopen session after 12 hours"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/attendance/reopen-session",
                            headers=headers, json={"session_id": session_id})
    
    if response.status_code == 200:
        print(f"\n✅ Session reopened successfully")
        print(f"  Message: {response.json().get('message')}")
        return True
    else:
        data = response.json()
        print(f"\n⚠️ Cannot reopen session:")
        print(f"  Error: {data.get('error')}")
        print(f"  Message: {data.get('message')}")
        if data.get('hours_remaining'):
            print(f"  Hours Remaining: {data['hours_remaining']:.1f}")
        return False

def test_workflow():
    """Test complete workflow"""
    print("="*60)
    print("SESSION MANAGEMENT TEST")
    print("="*60)
    
    # 1. Login
    token = login()
    if not token:
        return
    
    # 2. Get existing sessions
    print("\n" + "="*60)
    print("STEP 1: Get Existing Sessions")
    print("="*60)
    sessions = get_sessions(token)
    
    # 3. Start new test session
    print("\n" + "="*60)
    print("STEP 2: Start New Test Session")
    print("="*60)
    session_id = start_test_session(token)
    if not session_id:
        return
    
    # 4. Stop camera (daily end)
    print("\n" + "="*60)
    print("STEP 3: Stop Camera (Daily End)")
    print("="*60)
    stop_camera(token, session_id)
    
    # 5. Try to reopen immediately (should fail)
    print("\n" + "="*60)
    print("STEP 4: Try to Reopen Immediately (Should Fail)")
    print("="*60)
    reopen_session(token, session_id)
    
    # 6. Check session status
    print("\n" + "="*60)
    print("STEP 5: Check Session Status")
    print("="*60)
    get_sessions(token)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n📝 Notes:")
    print("  - Session is now in 'stopped_daily' status")
    print("  - Cannot reopen until 12 hours have passed")
    print("  - To test reopen, manually update end_time in database:")
    print(f"    UPDATE sessions SET end_time = DATE_SUB(NOW(), INTERVAL 13 HOUR) WHERE id = {session_id};")
    print("  - Then run: reopen_session(token, session_id)")

if __name__ == "__main__":
    test_workflow()
