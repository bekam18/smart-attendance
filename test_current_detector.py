#!/usr/bin/env python3
"""
Test Current Face Detector Configuration
"""

import sys
import os
sys.path.append('backend')

def test_current_detector():
    print("🔍 Testing current face detector configuration...")
    
    try:
        # Test the improved detector (used by attendance system)
        from recognizer.detector_improved import get_face_detector
        
        print("📦 Loading improved detector with InsightFace...")
        detector = get_face_detector(method='insightface')
        
        print(f"✅ Detector loaded: {detector.__class__.__name__}")
        print(f"📊 Method: {detector.method}")
        
        # Test detection
        import numpy as np
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        print("🔍 Testing face detection...")
        results = detector.detect_faces(test_img, return_confidence=True)
        
        print(f"✅ Detection test completed")
        print(f"📊 Results: {len(results)} faces detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_current_detector()