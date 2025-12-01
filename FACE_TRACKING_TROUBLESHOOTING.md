# Face Tracking Troubleshooting Guide

## Issue: Face Box Not Showing on Frontend

### Debugging Steps

#### 1. Check Browser Console
Open browser DevTools (F12) and check the Console tab for:

**Expected logs when camera starts:**
```
Video metadata loaded, starting face detection...
Sending face detection request...
Face detection response: {status: 'success', faces: [...]}
Face detected at: {x: 120, y: 80, w: 200, h: 250}
Drawing face box at: {x: 120, y: 80, w: 200, h: 250}
Drawing box: x=120, y=80, w=200, h=250, canvas=640x480
```

**Common errors to look for:**
- `401 Unauthorized` - JWT token expired or invalid
- `404 Not Found` - Backend endpoint not registered
- `500 Internal Server Error` - Backend face detection failed
- `Network Error` - Backend not running or CORS issue

#### 2. Verify Backend is Running
```bash
# Check if backend is running on port 5000
curl http://localhost:5000/attendance/test-ping
```

Expected response:
```json
{"status": "ok", "message": "Attendance blueprint is working"}
```

#### 3. Test Face Detection Endpoint Manually

**Using curl (Windows CMD):**
```cmd
curl -X POST http://localhost:5000/attendance/detect-face ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -F "image=@test_image.jpg"
```

**Expected response:**
```json
{
  "status": "success",
  "faces": [
    {
      "bbox": {"x": 120, "y": 80, "w": 200, "h": 250},
      "landmarks": [[x1,y1], [x2,y2], [x3,y3], [x4,y4], [x5,y5]]
    }
  ],
  "count": 1
}
```

#### 4. Check JWT Token
In browser console, check if token is valid:
```javascript
localStorage.getItem('token')
```

If null or expired, log in again.

#### 5. Verify Canvas Overlay
In browser console, check canvas element:
```javascript
// Check if overlay canvas exists
document.querySelector('canvas')

// Check canvas dimensions
const canvas = document.querySelector('canvas');
console.log(canvas.width, canvas.height);

// Manually draw test box
const ctx = canvas.getContext('2d');
ctx.strokeStyle = '#FF0000';
ctx.lineWidth = 5;
ctx.strokeRect(100, 100, 200, 200);
```

If you see a red box, the canvas is working.

#### 6. Check Video Element
```javascript
const video = document.querySelector('video');
console.log('Video ready:', video.readyState); // Should be 4
console.log('Video dimensions:', video.videoWidth, video.videoHeight);
```

### Common Issues and Solutions

#### Issue 1: "401 Unauthorized" Error
**Cause:** JWT token expired or missing

**Solution:**
1. Log out and log back in
2. Check token in localStorage
3. Verify token is being sent in API headers

#### Issue 2: "No face detected" in Console
**Cause:** Backend detector not finding faces

**Solutions:**
1. Ensure good lighting
2. Face camera directly
3. Move closer to camera
4. Check if InsightFace is installed:
   ```bash
   cd backend
   python -c "import insightface; print('✓ InsightFace installed')"
   ```

#### Issue 3: Canvas Overlay Not Visible
**Cause:** CSS z-index or positioning issue

**Solution:**
Check in browser DevTools:
1. Inspect the canvas element
2. Verify `position: absolute` is applied
3. Verify `z-index: 10` is set
4. Check if canvas is behind video

#### Issue 4: Box Appears But Doesn't Move
**Cause:** Detection not updating or smoothing stuck

**Solution:**
1. Check console for repeated detection requests
2. Verify `lastFaceBoxRef.current` is updating
3. Check if `updateOverlay` animation loop is running

#### Issue 5: Backend Returns 500 Error
**Cause:** InsightFace detector initialization failed

**Solution:**
```bash
cd backend
python -c "from recognizer.detector_insightface import face_detector; print('✓ Detector loaded')"
```

If error, reinstall InsightFace:
```bash
pip install insightface onnxruntime
```

#### Issue 6: CORS Error
**Cause:** Frontend and backend on different origins

**Solution:**
Check `backend/app.py` has CORS enabled:
```python
from flask_cors import CORS
CORS(app)
```

### Manual Testing

#### Test 1: Draw Static Box
Add this to `updateOverlay()` function temporarily:
```typescript
// Test: Draw a static red box
context.strokeStyle = '#FF0000';
context.lineWidth = 5;
context.strokeRect(100, 100, 200, 200);
```

If you see a red box, canvas rendering works.

#### Test 2: Simulate Face Detection
Add this to `startCamera()` after video loads:
```typescript
// Test: Simulate face detection
lastFaceBoxRef.current = {
  x: 150,
  y: 100,
  w: 200,
  h: 250
};
setFaceDetected(true);
```

If you see a green box, the drawing logic works.

#### Test 3: Check API Response
Add this to `detectFacesFromBackend()`:
```typescript
console.log('API Response:', JSON.stringify(data, null, 2));
```

Verify the response structure matches expected format.

### Performance Checks

#### Check Detection Rate
```javascript
let detectionCount = 0;
setInterval(() => {
  console.log(`Detections per second: ${detectionCount / 5}`);
  detectionCount = 0;
}, 5000);

// In detectFacesFromBackend, add:
detectionCount++;
```

Expected: ~2 detections per second (500ms interval)

#### Check Render Rate
```javascript
let frameCount = 0;
setInterval(() => {
  console.log(`FPS: ${frameCount}`);
  frameCount = 0;
}, 1000);

// In updateOverlay, add:
frameCount++;
```

Expected: ~60 FPS

### Quick Fixes

#### Fix 1: Force Canvas Redraw
```typescript
// In updateOverlay, before clearing:
canvas.style.display = 'none';
canvas.offsetHeight; // Force reflow
canvas.style.display = 'block';
```

#### Fix 2: Increase Detection Frequency
```typescript
// Change from 500ms to 200ms
detectionIntervalRef.current = setInterval(() => {
  detectFacesFromBackend();
}, 200);
```

#### Fix 3: Disable Smoothing (for testing)
```typescript
// In updateOverlay:
if (lastFaceBoxRef.current) {
  // Use raw box without smoothing
  drawFaceBox(context, lastFaceBoxRef.current);
}
```

#### Fix 4: Add Fallback Static Box
```typescript
// If no face detected for 3 seconds, show guide box
if (!lastFaceBoxRef.current) {
  const guideBox = {
    x: canvas.width * 0.3,
    y: canvas.height * 0.25,
    w: canvas.width * 0.4,
    h: canvas.height * 0.5
  };
  context.strokeStyle = '#FFFF00'; // Yellow
  context.setLineDash([10, 5]); // Dashed line
  context.strokeRect(guideBox.x, guideBox.y, guideBox.w, guideBox.h);
  context.setLineDash([]); // Reset
}
```

### Verification Checklist

- [ ] Backend server running on port 5000
- [ ] InsightFace installed and working
- [ ] JWT token valid and not expired
- [ ] Camera permissions granted
- [ ] Video element playing (readyState = 4)
- [ ] Canvas overlay positioned correctly
- [ ] Console shows detection requests
- [ ] Console shows detection responses
- [ ] Console shows drawing commands
- [ ] No JavaScript errors in console
- [ ] No network errors in Network tab

### Still Not Working?

1. **Clear browser cache** and reload
2. **Try different browser** (Chrome, Firefox, Edge)
3. **Check firewall** isn't blocking localhost:5000
4. **Restart backend server**
5. **Check backend logs** for errors
6. **Verify video codec** support in browser

### Get More Help

If still not working, provide:
1. Browser console logs (full output)
2. Network tab showing API requests/responses
3. Backend terminal output
4. Browser and OS version
5. Screenshot of the issue
