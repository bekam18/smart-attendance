"""
Test script for InsightFace detector
Tests detection, alignment, and performance
"""

import cv2
import numpy as np
import time
from recognizer.detector import face_detector

def test_detection():
    """Test face detection on sample images"""
    print("="*60)
    print("Testing InsightFace Detector")
    print("="*60)
    print()
    
    # Test with webcam
    print("Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
    
    print("✅ Webcam opened")
    print()
    print("Press 'q' to quit, 's' to save detection")
    print("="*60)
    print()
    
    frame_count = 0
    total_time = 0
    detections_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Detect faces
        start_time = time.time()
        faces = face_detector.detect_faces(frame)
        detection_time = time.time() - start_time
        
        frame_count += 1
        total_time += detection_time
        
        # Draw bounding boxes
        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw label
            label = f"Face {i+1}"
            cv2.putText(frame, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Extract and show aligned face
            try:
                aligned_face = face_detector.extract_face(frame, (x, y, w, h), face_index=i)
                
                # Show aligned face in corner
                h_face, w_face = aligned_face.shape[:2]
                y_offset = i * (h_face + 10) + 10
                x_offset = frame.shape[1] - w_face - 10
                
                if y_offset + h_face < frame.shape[0]:
                    frame[y_offset:y_offset+h_face, x_offset:x_offset+w_face] = aligned_face
            except Exception as e:
                print(f"Error extracting face {i}: {e}")
        
        detections_count += len(faces)
        
        # Display stats
        fps = 1.0 / detection_time if detection_time > 0 else 0
        avg_time = total_time / frame_count if frame_count > 0 else 0
        
        stats_text = [
            f"Detector: {face_detector.method}",
            f"Faces: {len(faces)}",
            f"FPS: {fps:.1f}",
            f"Avg Time: {avg_time*1000:.1f}ms"
        ]
        
        y_pos = 30
        for text in stats_text:
            cv2.putText(frame, text, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_pos += 25
        
        # Show frame
        cv2.imshow('InsightFace Detector Test', frame)
        
        # Handle key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f'detection_test_{int(time.time())}.jpg'
            cv2.imwrite(filename, frame)
            print(f"✅ Saved: {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Print summary
    print()
    print("="*60)
    print("Test Summary")
    print("="*60)
    print(f"Frames processed: {frame_count}")
    print(f"Total detections: {detections_count}")
    print(f"Average time per frame: {avg_time*1000:.2f}ms")
    print(f"Average FPS: {1.0/avg_time:.2f}" if avg_time > 0 else "N/A")
    print("="*60)


def test_alignment():
    """Test face alignment quality"""
    print()
    print("="*60)
    print("Testing Face Alignment")
    print("="*60)
    print()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
    
    print("Move your head to test alignment at different angles")
    print("Press 'q' to quit")
    print()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Detect faces
        faces = face_detector.detect_faces(frame)
        
        if len(faces) > 0:
            # Take first face
            x, y, w, h = faces[0]
            
            # Extract aligned face
            aligned_face = face_detector.extract_face(frame, (x, y, w, h), face_index=0)
            
            # Show original crop vs aligned
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Resize aligned face for display
            display_face = cv2.resize(aligned_face, (200, 200))
            
            # Show in corner
            frame[10:210, frame.shape[1]-210:frame.shape[1]-10] = display_face
            
            cv2.putText(frame, "Aligned Face", 
                       (frame.shape[1]-200, 220),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow('Alignment Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        print()
        print("InsightFace Detector Test")
        print()
        
        # Check detector method
        print(f"Current detector: {face_detector.method}")
        print()
        
        if face_detector.method != 'insightface':
            print("⚠️  Warning: Not using InsightFace detector!")
            print(f"Current method: {face_detector.method}")
            print()
        
        # Run tests
        test_detection()
        
        # Optional: Test alignment
        response = input("\nTest alignment? (y/n): ")
        if response.lower() == 'y':
            test_alignment()
        
        print("\n✅ Testing complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
