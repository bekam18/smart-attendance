# Debug Bounding Box - Step by Step

## Changes Made

I've added aggressive debugging to help us see what's happening:

### 1. Red Border Around Canvas
The canvas now has a **red border** so you can see if it's positioned correctly over the video.

### 2. Test Red Box
A small **red box** is drawn at position (10, 10) on every frame to verify the canvas is rendering.

### 3. Console Logging
Every step now logs to console:
- Video dimensions
- Canvas sizing
- Face detection results
- Drawing operations

## Testing Steps

### Step 1: Hard Refresh Browser
**IMPORTANT:** You MUST do a hard refresh to see changes:
- **Windows/Linux:** `Ctrl + Shift + R` or `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`

### Step 2: Open Browser Console
- Press `F12` to open DevTools
- Go to the **Console** tab
- Keep it open while testing

### Step 3: Start Camera
1. Click "Start Camera" button
2. Allow camera access

### Step 4: Check What You See

#### ✅ If you see a RED BORDER around the video:
- Canvas element is positioned correctly
- Continue to Step 5

#### ❌ If you DON'T see a red border:
- The canvas element is not rendering
- Check console for errors
- Make sure you did a hard refresh

### Step 5: Check for Red Test Box

#### ✅ If you see a small RED BOX in top-left corner:
- Canvas is rendering correctly
- Drawing operations work
- Continue to Step 6

#### ❌ If you DON'T see the red test box:
- Canvas is not drawing
- Check console for errors
- Look for messages like "❌ updateOverlay: No context"

### Step 6: Check Console Logs

You should see logs like:
```
✅ Video metadata loaded
📹 Native: 640x480
📺 Display: 640x480
🔍 Video display: 640x480, native: 640x480
📐 Canvas resized to DISPLAY size: 640x480
🔴 Drew test red box at (10,10)
🔍 Checking lastFaceBoxRef: null
```

### Step 7: Wait for Face Detection

After ~1 second, you should see:
```
Sending face detection request...
Face detection response: {...}
✅ Face detected at: {"x":338,"y":134,"w":212,"h":212}
📌 lastFaceBoxRef set to: {"x":338,"y":134,"w":212,"h":212}
```

Then:
```
🔍 Checking lastFaceBoxRef: {x: 338, y: 134, w: 212, h: 212}
🎨 Drawing box: native(338,134,212,212) → display(338,134,212,212) | scale(1.00,1.00)
```

### Step 8: Check for Green Box

#### ✅ If you see GREEN BOX around your face:
- **SUCCESS!** Everything is working

#### ❌ If you DON'T see green box but logs show face detected:
- Copy the console logs and share them
- We'll debug the drawing logic

## Alternative: Test with Standalone HTML

If the React app still doesn't work, test with the standalone file:

1. Open `test_canvas_debug.html` in your browser
2. Click "Start Camera"
3. Click "Draw Test Box" - you should see a green box
4. Click "Test Backend Detection" - it will call your backend

This will help isolate if the issue is:
- React-specific
- Backend-specific
- Browser/canvas-specific

## Common Issues

### Issue 1: Canvas Not Visible
**Symptom:** No red border, no red test box
**Solution:** 
- Hard refresh browser (Ctrl+Shift+R)
- Check if frontend dev server is running
- Check browser console for React errors

### Issue 2: Canvas Visible But No Drawing
**Symptom:** Red border visible, but no red test box
**Solution:**
- Check console for "❌ updateOverlay" errors
- Verify video.readyState = 4
- Check if animation loop is running

### Issue 3: Red Box Visible But No Green Box
**Symptom:** Red test box works, but no green face box
**Solution:**
- Check if backend detection is working
- Look for "✅ Face detected" in console
- Verify lastFaceBoxRef is being set
- Check if face is in frame and well-lit

### Issue 4: Backend Not Detecting Face
**Symptom:** Logs show "⚠️ No face detected"
**Solution:**
- Make sure your face is visible and well-lit
- Check backend logs for errors
- Test backend directly with `test_detect_face_endpoint.bat`

## What to Share

If it's still not working, share:

1. **Screenshot** of the browser showing:
   - The video feed
   - Whether red border is visible
   - Whether red test box is visible

2. **Console logs** from the moment you click "Start Camera"

3. **Network tab** showing the `/api/attendance/detect-face` request/response

This will help me identify exactly where the issue is.
