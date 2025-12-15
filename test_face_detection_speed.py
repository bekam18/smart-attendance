#!/usr/bin/env python3
"""Test face detection speed improvements"""

import time
import requests
import cv2
import numpy as np

def test_face_detection_speed():
    """Test the speed of face detection endpoint"""
    
    print("Testing Face Detection Speed Improvements")
    print("=" * 50)
    
    # Create a test image with a face (or use webcam)
    try:
        # Try to use webcam for real test
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access webcam, using synthetic image")
            # Create a synthetic face-like image
            img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        else:
            print("📹 Using webcam for real test")
            ret, img = cap.read()
            cap.release()
            if not ret:
                print("❌ Failed to capture from webcam")
                return
            
            # Resize to test resolution
            img = cv2.resize(img, (320, 240))
        
        # Convert to JPEG bytes
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 40])
        image_bytes = buffer.tobytes()
        
        print(f"📊 Test image size: {len(image_bytes)} bytes")
        print(f"📐 Image dimensions: {img.shape}")
        
        # Test multiple requests to measure average speed
        base_url = "http://127.0.0.1:5000/api"
        
        # You'll need a valid JWT token for testing
        # For now, we'll just test the endpoint availability
        
        times = []
        for i in range(5):
            print(f"\n🔍 Test {i+1}/5:")
            
            start_time = time.time()
            
            try:
                # Prepare the request
                files = {'image': ('test.jpg', image_bytes, 'image/jpeg')}
                
                # Make request (this will fail without auth, but we can measure network time)
                response = requests.post(
                    f"{base_url}/attendance/detect-face",
                    files=files,
                    timeout=3
                )
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to ms
                
                print(f"   ⏱️  Response time: {duration:.1f}ms")
                print(f"   📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Faces detected: {data.get('count', 0)}")
                    times.append(duration)
                elif response.status_code == 401:
                    print(f"   🔐 Authentication required (expected)")
                    times.append(duration)  # Still measure network time
                else:
                    print(f"   ❌ Error: {response.text}")
                
            except requests.exceptions.Timeout:
                print(f"   ⏰ Request timed out (>3000ms)")
            except requests.exceptions.ConnectionError:
                print(f"   🔌 Connection failed - is the server running?")
                break
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Small delay between requests
            time.sleep(0.5)
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n📈 Performance Summary:")
            print(f"   Average: {avg_time:.1f}ms")
            print(f"   Fastest: {min_time:.1f}ms")
            print(f"   Slowest: {max_time:.1f}ms")
            
            # Performance assessment
            if avg_time < 500:
                print(f"   🚀 Excellent performance!")
            elif avg_time < 1000:
                print(f"   ✅ Good performance")
            elif avg_time < 2000:
                print(f"   ⚠️  Acceptable performance")
            else:
                print(f"   ❌ Slow performance - needs optimization")
        
        print(f"\n💡 Optimization Tips:")
        print(f"   - Reduced image resolution to 320x240 for speed")
        print(f"   - Lowered JPEG quality to 40% for faster upload")
        print(f"   - Reduced detection interval to 1 second")
        print(f"   - Increased smoothing factor to 0.6 for responsive tracking")
        print(f"   - Added client-side detection fallback if available")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_face_detection_speed()