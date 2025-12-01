# Real-Time Face Tracking Implementation

## Overview
The camera preview now features **dynamic face tracking** with bounding boxes that follow detected faces in real-time, replacing the previous static guide box.

## What Changed

### Backend Changes
**New Endpoint: `/attendance/detect-face`**
- Returns face bounding boxes and landmarks from InsightFace detector
- Lightweight endpoint optimized for real-time detection
- Returns JSON with face coordinates and optional 5-point landmarks

**Response Format:**
```json
{
  "status": "success",
  "faces": [
    {
      "bbox": {
        "x": 120,
        "y": 80,
        "w": 200,
        "h": 250
      },
      "landmarks": [[x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5]]
    }
  ],
  "count": 1
}
```

### Frontend Changes
**CameraPreview Component (`frontend/src/components/CameraPreview.tsx`)**

1. **Removed Static Box**
   - Eliminated the fixed green rectangle in the center
   - No more "Position face here" label

2. **Added Dynamic Face Tracking**
   - Calls `/attendance/detect-face` every 500ms
   - Updates overlay canvas at 60fps for smooth animation
   - Bounding box follows face movement in real-time

3. **Smooth Animation**
   - Exponential moving average (EMA) smoothing
   - Prevents jittery box movement
   - Configurable smoothing factor (alpha = 0.3)

4. **Visual Features**
   - Green bounding box around detected face
   - Corner markers for better visibility
   - Optional landmark points (5 facial keypoints)
   - "Face Detected" badge only shows when face is present

5. **No Face Handling**
   - Box disappears when no face detected
   - Badge removed automatically
   - Clean overlay with no artifacts

## How It Works

### Detection Flow
```
1. Camera captures video stream (640x480)
2. Every 500ms: Send frame to backend for detection
3. Backend returns face bounding box + landmarks
4. Frontend stores detection result
5. Every 16ms (60fps): Update overlay canvas
   - Apply smoothing to box coordinates
   - Draw box and corner markers
   - Draw landmarks (optional)
```

### Smoothing Algorithm
```typescript
smoothed_x = previous_x + alpha * (new_x - previous_x)
```
- `alpha = 0.3` provides good balance between responsiveness and smoothness
- Lower alpha = smoother but slower response
- Higher alpha = faster but more jittery

## Performance

- **Detection Rate:** 2 FPS (every 500ms)
- **Render Rate:** 60 FPS (smooth animation)
- **Network:** ~10-20 KB per detection request
- **CPU:** Minimal frontend overhead

## Usage

The face tracking works automatically when the camera is started:

1. Click "Start Camera"
2. Face detection begins immediately
3. Green box appears and follows your face
4. Move around - box tracks your movement
5. "Face Detected" badge shows when face is visible

## Testing

Run the test script:
```bash
test_face_detection.bat
```

Or test manually:
1. Start the backend server
2. Open the attendance session page
3. Start the camera
4. Move your face around - box should follow smoothly

## Technical Details

### Backend
- Uses InsightFace RetinaFace detector
- Returns bounding boxes in (x, y, w, h) format
- Includes 5-point landmarks (eyes, nose, mouth corners)
- JWT authentication required

### Frontend
- Two-layer canvas system:
  - Video canvas (hidden, for capture)
  - Overlay canvas (visible, for tracking box)
- RequestAnimationFrame for smooth 60fps rendering
- Separate interval for backend detection calls
- Automatic cleanup on camera stop

## Configuration

### Adjust Detection Frequency
In `CameraPreview.tsx`, change the interval:
```typescript
detectionIntervalRef.current = setInterval(() => {
  detectFacesFromBackend();
}, 500); // Change this value (milliseconds)
```

### Adjust Smoothing
In `CameraPreview.tsx`, modify the alpha parameter:
```typescript
const smoothed = smoothBox(lastFaceBoxRef.current, 0.3); // Change 0.3
```
- Lower (0.1-0.2): Very smooth, slower response
- Higher (0.5-0.7): Fast response, less smooth

### Toggle Landmarks
Landmarks are drawn automatically if returned by backend. To disable, comment out the landmark drawing code in `drawFaceBox()`.

## Benefits

1. **Better User Experience**
   - Visual feedback that face is detected
   - Helps users position themselves correctly
   - Professional appearance

2. **Real-Time Feedback**
   - Immediate response to face movement
   - Smooth, non-jittery tracking
   - Clear indication when face is lost

3. **Accurate Detection**
   - Uses production InsightFace detector
   - Same detector used for recognition
   - Consistent with attendance recording

4. **Performance Optimized**
   - Efficient detection rate (2 FPS)
   - Smooth rendering (60 FPS)
   - Minimal network overhead

## Troubleshooting

**Box is jittery:**
- Decrease alpha value for more smoothing
- Increase detection interval to reduce updates

**Box lags behind face:**
- Increase alpha value for faster response
- Decrease detection interval for more frequent updates

**No box appears:**
- Check browser console for errors
- Verify backend is running
- Check JWT token is valid
- Ensure camera permissions granted

**Box appears but doesn't move:**
- Check network tab for detection API calls
- Verify backend returns valid bbox data
- Check console for JavaScript errors

## Future Enhancements

Possible improvements:
- Multiple face tracking
- Face quality indicators (blur, lighting)
- Distance estimation (too close/far)
- Pose estimation (face angle)
- Confidence visualization
