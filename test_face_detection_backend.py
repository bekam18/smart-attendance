#!/usr/bin/env python3
"""
Test the face detection backend API directly
"""

import requests
import cv2
import numpy as np
import base64
import json
import sys
import os

def test_face_detection_api():
    """Test the face detection API with a sample image"""
    
    print("🔍 Testing Face Detection Backend API")
    print("=" * 50)
    
    # Backend URL
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Check if backend is running
    print("\n1. Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/api/debug/echo", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Create a test image with a face-like pattern
    print("\n2. Creating test image...")
    try:
        # Create a simple test image (640x480)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw a simple face-like pattern
        # Face oval
        cv2.ellipse(img, (320, 240), (100, 130), 0, 0, 360, (200, 180, 160), -1)
        
        # Eyes
        cv2.circle(img, (290, 210), 15, (50, 50, 50), -1)
        cv2.circle(img, (350, 210), 15, (50, 50, 50), -1)
        
        # Nose
        cv2.circle(img, (320, 240), 8, (150, 130, 120), -1)
        
        # Mouth
        cv2.ellipse(img, (320, 270), (25, 15), 0, 0, 180, (100, 80, 80), 2)
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        print("✅ Test image created")
        print(f"   Image size: {img.shape}")
        print(f"   JPEG size: {len(buffer)} bytes")
        
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return False
    
    # Test 3: Test face detection API without authentication
    print("\n3. Testing face detection API (no auth)...")
    try:
        files = {'image': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
        response = requests.post(f"{base_url}/api/attendance/detect-face", files=files, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("⚠️  Authentication required (expected)")
        elif response.status_code == 200:
            data = response.json()
            print("✅ Face detection successful (no auth required)")
            print(f"   Result: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 4: Test with a real webcam capture if available
    print("\n4. Testing with webcam capture...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️  No webcam available")
        else:
            ret, frame = cap.read()
            if ret:
                # Resize to match frontend processing
                frame_small = cv2.resize(frame, (160, 120))
                
                # Encode as JPEG with low quality (matching frontend)
                _, buffer_real = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 20])
                
                print("✅ Webcam capture successful")
                print(f"   Original size: {frame.shape}")
                print(f"   Processed size: {frame_small.shape}")
                print(f"   JPEG size: {len(buffer_real)} bytes")
                
                # Test API with real image (no auth)
                files = {'image': ('webcam.jpg', buffer_real.tobytes(), 'image/jpeg')}
                response = requests.post(f"{base_url}/api/attendance/detect-face", files=files, timeout=10)
                
                print(f"   API Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Real face detection successful")
                    print(f"   Result: {json.dumps(data, indent=2)}")
                elif response.status_code == 401:
                    print("⚠️  Authentication required")
                else:
                    print(f"   Response: {response.text[:200]}...")
                    
            cap.release()
            
    except Exception as e:
        print(f"⚠️  Webcam test failed: {e}")
    
    # Test 5: Check face detector model status
    print("\n5. Testing model status...")
    try:
        response = requests.get(f"{base_url}/api/debug/model-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Model status retrieved")
            print(f"   Status: {json.dumps(data, indent=2)}")
        else:
            print(f"⚠️  Model status unavailable: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Model status check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Face Detection Backend Test Complete")
    
    return True

if __name__ == "__main__":
    test_face_detection_api()