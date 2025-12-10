#!/usr/bin/env python3
"""
Test InsightFace Installation and Performance
"""

import sys
import time
import cv2
import numpy as np

def test_insightface_installation():
    """Test if InsightFace is properly installed"""
    print("🔍 Testing InsightFace installation...")
    
    try:
        from insightface.app import FaceAnalysis
        print("✅ InsightFace imported successfully")
        
        # Initialize detector
        print("🔧 Initializing InsightFace detector...")
        app = FaceAnalysis(
            name='buffalo_l',
            providers=['CPUExecutionProvider'],
            allowed_modules=['detection']
        )
        
        app.prepare(ctx_id=-1, det_size=(320, 320))
        print("✅ InsightFace detector initialized successfully")
        
        # Test with a sample image
        print("🖼️ Testing face detection...")
        
        # Create a test image (640x480 with a simple face-like pattern)
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        test_img[100:300, 200:400] = [100, 100, 100]  # Gray rectangle (face area)
        
        start_time = time.time()
        faces = app.get(test_img)
        detection_time = time.time() - start_time
        
        print(f"✅ Detection completed in {detection_time:.3f} seconds")
        print(f"📊 Found {len(faces)} faces")
        
        if len(faces) > 0:
            for i, face in enumerate(faces):
                bbox = face.bbox
                confidence = face.det_score
                print(f"   Face {i+1}: bbox={bbox}, confidence={confidence:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ InsightFace not installed: {e}")
        print("💡 Install with: pip install insightface")
        return False
    except Exception as e:
        print(f"❌ InsightFace initialization failed: {e}")
        print("💡 Try: pip install --upgrade insightface")
        return False

def test_opencv_fallback():
    """Test OpenCV fallback detector"""
    print("\n🔍 Testing OpenCV fallback detector...")
    
    try:
        # Load OpenCV's DNN face detector
        net = cv2.dnn.readNetFromTensorflow(
            'opencv_face_detector_uint8.pb',
            'opencv_face_detector.pbtxt'
        )
        print("✅ OpenCV DNN detector loaded")
        return True
    except Exception as e:
        print(f"⚠️ OpenCV DNN detector not available: {e}")
        
        # Try Haar Cascade as last resort
        try:
            cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("✅ OpenCV Haar Cascade detector loaded (basic)")
            return True
        except Exception as e2:
            print(f"❌ No face detectors available: {e2}")
            return False

def main():
    print("🚀 Face Detection Setup Test")
    print("=" * 50)
    
    # Test InsightFace
    insightface_ok = test_insightface_installation()
    
    if not insightface_ok:
        print("\n⚠️ InsightFace not working, testing fallback options...")
        opencv_ok = test_opencv_fallback()
        
        if not opencv_ok:
            print("\n❌ No face detection methods available!")
            print("💡 Please install InsightFace: pip install insightface")
            sys.exit(1)
        else:
            print("\n✅ OpenCV fallback available")
    else:
        print("\n🎉 InsightFace is working perfectly!")
        print("💡 Your system is ready for high-accuracy face detection")
    
    print("\n📋 Recommendations:")
    print("   • For best performance: Use InsightFace (current setup)")
    print("   • Detection size: 320x320 (good balance of speed/accuracy)")
    print("   • Confidence threshold: 0.3+ (reduces false positives)")
    print("   • Processing interval: 3-4 seconds (reduces CPU load)")

if __name__ == "__main__":
    main()