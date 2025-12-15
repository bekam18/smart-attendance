#!/usr/bin/env python3
"""Debug face detection issues"""

import sys
import os
sys.path.append('backend')

def test_face_detection_dependencies():
    """Test if face detection dependencies are working"""
    
    print("🔍 Testing Face Detection Dependencies")
    print("=" * 50)
    
    # Test 1: Check if recognizer modules exist
    print("\n1. Checking recognizer modules...")
    
    try:
        import backend.recognizer.detector_improved as detector_improved
        print("   ✅ detector_improved module found")
    except ImportError as e:
        print(f"   ❌ detector_improved module missing: {e}")
        return False
    
    # Test 2: Check if get_face_detector function works
    print("\n2. Testing get_face_detector function...")
    
    try:
        from backend.recognizer.detector_improved import get_face_detector
        print("   ✅ get_face_detector function imported")
        
        # Try to initialize detector
        detector = get_face_detector(method='insightface')
        print("   ✅ InsightFace detector initialized")
        
    except Exception as e:
        print(f"   ❌ Detector initialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test with a simple image
    print("\n3. Testing face detection with sample image...")
    
    try:
        import numpy as np
        import cv2
        
        # Create a simple test image (random noise)
        test_image = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        print(f"   ✅ Test image created: {test_image.shape}")
        
        # Try detection
        results = detector.detect_faces(test_image, return_confidence=True)
        print(f"   ✅ Detection completed: {len(results)} faces found")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_server():
    """Test if backend server is running and accessible"""
    
    print("\n🌐 Testing Backend Server")
    print("=" * 30)
    
    try:
        import requests
        
        # Test server health
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"   ✅ Server responding: {response.status_code}")
        
        # Test if detect-face endpoint exists (will fail auth but should return 401, not 404)
        response = requests.post("http://127.0.0.1:5000/api/attendance/detect-face", timeout=5)
        if response.status_code == 401:
            print(f"   ✅ detect-face endpoint exists (auth required)")
        elif response.status_code == 404:
            print(f"   ❌ detect-face endpoint not found")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to server - is it running?")
        return False
    except Exception as e:
        print(f"   ❌ Server test failed: {e}")
        return False

def check_file_structure():
    """Check if required files exist"""
    
    print("\n📁 Checking File Structure")
    print("=" * 30)
    
    required_files = [
        'backend/recognizer/detector_improved.py',
        'backend/blueprints/attendance.py',
        'backend/app.py',
        'frontend/src/components/CameraPreview.tsx'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all diagnostic tests"""
    
    print("🚀 SmartAttendance Face Detection Diagnostics")
    print("=" * 60)
    
    # Run tests
    files_ok = check_file_structure()
    deps_ok = test_face_detection_dependencies() if files_ok else False
    server_ok = test_backend_server()
    
    print(f"\n📊 Diagnostic Summary")
    print("=" * 30)
    print(f"   File Structure: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"   Dependencies:   {'✅ OK' if deps_ok else '❌ ISSUES'}")
    print(f"   Backend Server: {'✅ OK' if server_ok else '❌ ISSUES'}")
    
    if files_ok and deps_ok and server_ok:
        print(f"\n🎉 All systems operational!")
        print(f"   Face detection should be working properly.")
    else:
        print(f"\n⚠️  Issues detected!")
        print(f"   Please fix the issues above before testing face detection.")
        
        if not files_ok:
            print(f"\n💡 File Structure Issues:")
            print(f"   - Make sure you're running from the project root directory")
            print(f"   - Check if all required files are present")
        
        if not deps_ok:
            print(f"\n💡 Dependency Issues:")
            print(f"   - Install required packages: pip install -r backend/requirements.txt")
            print(f"   - Check if InsightFace is properly installed")
            print(f"   - Verify Python path and imports")
        
        if not server_ok:
            print(f"\n💡 Server Issues:")
            print(f"   - Start the backend server: cd backend && python app.py")
            print(f"   - Check if port 5000 is available")
            print(f"   - Verify server configuration")

if __name__ == "__main__":
    main()