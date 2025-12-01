# Face Tracking Quick Start Guide

## ✅ Implementation Complete

The face tracking feature is now fully implemented with:
- ✅ Backend API endpoint for face detection
- ✅ Frontend dynamic bounding box overlay
- ✅ Smooth animation at 60fps
- ✅ Real-time tracking that follows face movement

## 🚀 Quick Test (3 Steps)

### Step 1: Test Standalone (No Backend Required)
```bash
# Open this file in your browser
test_face_tracking.html
```

Click "Start Camera" → You should see a green box moving around (simulated)

### Step 2: Test Backend Endpoint
```bash
# In terminal
cd backend
python -c "from blueprints.attendance import detect_face; print('✓ Endpoint loaded')"
```

### Step 3: Test in Application
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Login as instructor
4. Go to attendance session
5. Click "Start Camera"
6. **Look for green box around your face**

## 🔍 Debugging (If Box Not Showing)

### Quick Check #1: Browser Console
Press F12, look for these logs:
```
✓ Video metadata loaded, starting face detection...
✓ Sending face detection request...
✓ Face detection response: {status: 'success', ...}
✓ Face detected at: {x: ..., y: ..., w: ..., h: ...}
✓ Drawing face box at: {x: ..., y: ..., w: ..., h: ...}
```

**If you see these logs:** Implementation is working! Box should be visible.

**If you see errors:** Note the error message and check troubleshooting guide.

### Quick Check #2: Manual Canvas Test
In browser console (F12):
```javascript
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
ctx.strokeStyle = '#FF0000';
ctx.lineWidth = 10;
ctx.strokeRect(50, 50, 300, 300);
```

**If you see a red box:** Canvas rendering works, issue is with detection.

**If no red box:** Canvas element issue, check positioning/z-index.

### Quick Check #3: Backend Test
```bash
curl http://localhost:5000/attendance/test-ping
```

**Expected:** `{"status": "ok", "message": "Attendance blueprint is working"}`

**If error:** Backend not running or wrong port.

## 📋 Common Issues & Instant Fixes

| Issue | Instant Fix |
|-------|-------------|
| "401 Unauthorized" | Log out and log back in |
| "No face detected" | Improve lighting, face camera directly |
| Box not visible | Check browser console for errors |
| Box doesn't move | Check Network tab for API calls |
| Canvas not showing | Inspect element, verify z-index: 10 |

## 📁 Key Files

**Backend:**
- `backend/blueprints/attendance.py` - Face detection endpoint

**Frontend:**
- `frontend/src/components/CameraPreview.tsx` - Face tracking component

**Testing:**
- `test_face_tracking.html` - Standalone test page
- `test_face_detection.bat` - Backend test script

**Documentation:**
- `REAL_TIME_FACE_TRACKING.md` - Full feature docs
- `FACE_TRACKING_TROUBLESHOOTING.md` - Detailed debugging
- `FACE_TRACKING_IMPLEMENTATION_SUMMARY.md` - Technical details

## 🎯 Expected Behavior

When working correctly:

1. **Camera starts** → Video feed appears
2. **Face detected** → Green box appears around face
3. **Move face** → Box follows smoothly (no jitter)
4. **Move away** → Box disappears
5. **Return** → Box reappears

**Visual indicators:**
- Green bounding box with corner brackets
- "Face Detected" badge (top-right)
- Smooth movement (60fps animation)
- Optional: 5 green dots (facial landmarks)

## ⚙️ Configuration

### Change Detection Speed
```typescript
// In CameraPreview.tsx, line ~210
detectionIntervalRef.current = setInterval(() => {
  detectFacesFromBackend();
}, 500); // ← Change this (milliseconds)
```

**Faster (200ms):** More responsive, more network traffic
**Slower (1000ms):** Less responsive, less network traffic

### Change Smoothness
```typescript
// In CameraPreview.tsx, line ~180
const smoothed = smoothBox(lastFaceBoxRef.current, 0.3); // ← Change this
```

**Lower (0.1-0.2):** Very smooth, slower response
**Higher (0.5-0.7):** Fast response, less smooth

## 🆘 Still Not Working?

1. **Read full troubleshooting:** `FACE_TRACKING_TROUBLESHOOTING.md`
2. **Test standalone page:** `test_face_tracking.html`
3. **Check browser console:** Look for error messages
4. **Verify backend:** Ensure InsightFace is installed
5. **Check JWT token:** May need to re-login

## 📞 Support Checklist

If reporting an issue, provide:
- [ ] Browser console logs (full output)
- [ ] Network tab (show API requests/responses)
- [ ] Backend terminal output
- [ ] Browser and OS version
- [ ] Screenshot of the issue
- [ ] Result of standalone test page

## ✨ Success Indicators

You'll know it's working when:
- ✅ Green box appears around your face
- ✅ Box follows as you move
- ✅ Movement is smooth (not jumpy)
- ✅ "Face Detected" badge shows
- ✅ Console shows detection logs
- ✅ No errors in console

## 🎉 Next Steps

Once working:
1. Test with multiple users
2. Test in different lighting conditions
3. Test at different distances
4. Adjust detection/smoothing parameters
5. Consider adding enhancements (see IMPLEMENTATION_SUMMARY.md)

---

**Status:** ✅ Implementation complete and ready to test!

**Last Updated:** 2024
