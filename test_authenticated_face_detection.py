#!/usr/bin/env python3
"""
Test face detection API with authentication
"""

import requests
import cv2
import numpy as np
import json

def test_with_auth():
    """Test face detection with authentication"""
    
    print("🔍 Testing Authenticated Face Detection")
    print("=" * 50)
    
    # You need to get a valid JWT token first
    # This would normally come from logging in
    
    # For testing, let's try to login first
    login_data = {
        "username": "admin",  # Replace with actual admin username
        "password": "admin123"  # Replace with actual admin password
    }
    
    try:
        # Try to login
        login_response = requests.post(
            "http://127.0.0.1:5000/api/auth/login",
            json=login_data,
            timeout=5
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('token')
            print(f"✅ Login successful, got token")
            
            # Now test face detection with token
            # Create a test image
            img = np.zeros((240, 320, 3), dtype=np.uint8)
            
            # Draw a simple face-like pattern
            cv2.ellipse(img, (160, 120), (50, 65), 0, 0, 360, (200, 180, 160), -1)
            cv2.circle(img, (145, 105), 8, (50, 50, 50), -1)
            cv2.circle(img, (175, 105), 8, (50, 50, 50), -1)
            cv2.circle(img, (160, 120), 4, (150, 130, 120), -1)
            cv2.ellipse(img, (160, 135), (12, 8), 0, 0, 180, (100, 80, 80), 2)
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])
            
            # Test face detection API
            headers = {'Authorization': f'Bearer {token}'}
            files = {'image': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
            
            response = requests.post(
                "http://127.0.0.1:5000/api/attendance/detect-face",
                files=files,
                headers=headers,
                timeout=10
            )
            
            print(f"Face detection status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Face detection API working!")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if data.get('status') == 'success' and data.get('faces'):
                    print(f"✅ Detected {len(data['faces'])} face(s)")
                    for i, face in enumerate(data['faces']):
                        bbox = face['bbox']
                        confidence = face.get('confidence', 0)
                        print(f"  Face {i+1}: x={bbox['x']}, y={bbox['y']}, w={bbox['w']}, h={bbox['h']}, conf={confidence:.2f}")
                else:
                    print("⚠️ No faces detected in test image")
            else:
                print(f"❌ Face detection failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_with_auth()