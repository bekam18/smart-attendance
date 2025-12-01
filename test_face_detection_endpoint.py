"""
Test the face detection endpoint
"""
import requests
import cv2
import base64
import json

# Test image path (use a sample image with a face)
test_image_path = "backend/dataset/test_image.jpg"

# Read and encode image
try:
    img = cv2.imread(test_image_path)
    if img is None:
        print(f"❌ Could not read image from {test_image_path}")
        print("Please provide a test image with a face")
        exit(1)
    
    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', img)
    img_bytes = buffer.tobytes()
    
    print(f"✓ Image loaded: {img.shape}")
    print(f"✓ Image size: {len(img_bytes)} bytes")
    
except Exception as e:
    print(f"❌ Error loading image: {e}")
    exit(1)

# Test the endpoint
url = "http://localhost:5000/attendance/detect-face"

# You need to provide a valid JWT token
token = "YOUR_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    'image': ('test.jpg', img_bytes, 'image/jpeg')
}

print("\n" + "="*60)
print("Testing Face Detection Endpoint")
print("="*60)
print(f"URL: {url}")
print(f"Token: {token[:20]}..." if len(token) > 20 else f"Token: {token}")

try:
    response = requests.post(url, files=files, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print(f"\n✅ SUCCESS: Detected {data.get('count', 0)} face(s)")
            for i, face in enumerate(data.get('faces', [])):
                bbox = face.get('bbox', {})
                print(f"  Face {i+1}: x={bbox.get('x')}, y={bbox.get('y')}, w={bbox.get('w')}, h={bbox.get('h')}")
        else:
            print(f"\n⚠ No faces detected")
    else:
        print(f"\n❌ Request failed")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("="*60)
