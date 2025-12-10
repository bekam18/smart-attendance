#!/usr/bin/env python3
"""
Test script to verify face recognition performance improvements
"""

import time
import cv2
import numpy as np
from recognizer.detector_improved import get_face_detector

def test_detection_speed():
    """Test face detection speed with optimized settings"""
    print("🚀 Testing Face Detection Performance...")
    
    # Initialize detector
    detector = get_face_detector(method='insightface')
    
    # Create test image (640x480)
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Warm up (first detection is always slower)
    print("🔥 Warming up detector...")
    detector.detect_faces(test_img)
    
    # Test detection speed
    num_tests = 10
    total_time = 0
    
    print(f"⏱️ Running {num_tests} detection tests...")
    
    for i in range(num_tests):
        start_time = time.time()
        faces = detector.detect_faces(test_img, return_confidence=True)
        end_time = time.time()
        
        detection_time = end_time - start_time
        total_time += detection_time
        
        print(f"Test {i+1}: {detection_time:.3f}s - Found {len(faces)} faces")
    
    avg_time = total_time / num_tests
    print(f"\n📊 Results:")
    print(f"Average detection time: {avg_time:.3f}s")
    print(f"Target: < 1.0s ({'✅ PASS' if avg_time < 1.0 else '❌ FAIL'})")
    
    if avg_time < 0.5:
        print("🎉 Excellent performance!")
    elif avg_time < 1.0:
        print("✅ Good performance!")
    else:
        print("⚠️ Performance needs improvement")
    
    return avg_time

def test_with_real_camera():
    """Test with real camera feed"""
    print("\n📹 Testing with real camera...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    detector = get_face_detector(method='insightface')
    
    print("Press 'q' to quit, 's' to test detection speed")
    
    frame_count = 0
    detection_times = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Test detection every 30 frames (about 1 second at 30fps)
        if frame_count % 30 == 0:
            start_time = time.time()
            faces = detector.detect_faces(frame, return_confidence=True)
            detection_time = time.time() - start_time
            
            detection_times.append(detection_time)
            
            print(f"Frame {frame_count}: {detection_time:.3f}s - {len(faces)} faces")
            
            # Draw bounding boxes
            for face_data in faces:
                if isinstance(face_data, tuple):
                    bbox, confidence = face_data
                else:
                    bbox = face_data
                    confidence = 0.0
                
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"{confidence:.2f}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow('Performance Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Quick speed test
            start_time = time.time()
            faces = detector.detect_faces(frame, return_confidence=True)
            detection_time = time.time() - start_time
            print(f"Quick test: {detection_time:.3f}s - {len(faces)} faces")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if detection_times:
        avg_time = sum(detection_times) / len(detection_times)
        print(f"\n📊 Camera Test Results:")
        print(f"Average detection time: {avg_time:.3f}s")
        print(f"Total detections: {len(detection_times)}")

if __name__ == "__main__":
    print("🔧 Face Recognition Performance Test")
    print("=" * 50)
    
    # Test 1: Synthetic image speed
    avg_time = test_detection_speed()
    
    # Test 2: Real camera (optional)
    response = input("\nTest with real camera? (y/n): ").lower()
    if response == 'y':
        test_with_real_camera()
    
    print("\n✅ Performance testing complete!")
    print(f"Recommendation: {'System is optimized!' if avg_time < 1.0 else 'Consider further optimization'}")