# Canvas Overlay Debug Test

## Quick Test in Browser Console

When camera is running, paste this in browser console (F12):

```javascript
// Test 1: Check if canvas exists
const canvas = document.querySelector('canvas');
console.log('Canvas found:', canvas);
console.log('Canvas dimensions:', canvas?.width, 'x', canvas?.height);

// Test 2: Draw a test red box
if (canvas) {
  const ctx = canvas.getContext('2d');
  ctx.strokeStyle = 'red';
  ctx.lineWidth = 10;
  ctx.strokeRect(50, 50, 300, 300);
  console.log('✓ Red test box drawn at (50, 50, 300, 300)');
}

// Test 3: Check video dimensions
const video = document.querySelector('video');
console.log('Video dimensions:', video?.videoWidth, 'x', video?.videoHeight);
console.log('Video ready state:', video?.readyState);

// Test 4: Check if overlay canvas is the right one
const overlayCanvas = document.querySelectorAll('canvas');
console.log('Total canvases:', overlayCanvas.length);
overlayCanvas.forEach((c, i) => {
  console.log(`Canvas ${i}:`, c.className, c.style.cssText);
});
```

## Expected Results

**If working:**
- You should see a RED box on the video
- Canvas dimensions should match video (e.g., 640x480)
- Video ready state should be 4

**If not working:**
- Canvas might be 0x0 (not sized)
- Canvas might be behind video (z-index issue)
- Canvas might not exist

## Manual Fix Test

If red box doesn't show, try forcing canvas to front:

```javascript
const canvas = document.querySelector('canvas');
canvas.style.position = 'absolute';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.zIndex = '9999';
canvas.style.pointerEvents = 'none';

// Redraw test box
const ctx = canvas.getContext('2d');
ctx.clearRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = 'red';
ctx.lineWidth = 10;
ctx.strokeRect(50, 50, 300, 300);
```

## Simulate Face Detection

To test if the drawing logic works without backend:

```javascript
// Manually set a fake face box
const fakeBox = { x: 150, y: 100, w: 200, h: 250 };

// Get the canvas
const canvas = document.querySelectorAll('canvas')[0]; // First canvas (overlay)
const ctx = canvas.getContext('2d');

// Clear and draw
ctx.clearRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = 'lime';
ctx.lineWidth = 3;
ctx.strokeRect(fakeBox.x, fakeBox.y, fakeBox.w, fakeBox.h);

console.log('✓ Fake face box drawn');
```

## Check Detection Logs

Look for these in console:
```
Video metadata loaded, starting face detection...
Sending face detection request...
Face detection response: {...}
Face detected at: {x: ..., y: ..., w: ..., h: ...}
DRAW BOX: x=..., y=..., w=..., h=...
```

## Common Issues

### Issue: Canvas is 0x0
**Cause:** Video not loaded yet
**Fix:** Wait for video.readyState === 4

### Issue: Red test box shows but green box doesn't
**Cause:** Detection not returning data or coordinates wrong
**Fix:** Check console logs for detection response

### Issue: Nothing shows at all
**Cause:** Canvas behind video or not positioned
**Fix:** Check z-index and position styles

### Issue: Box shows in wrong place
**Cause:** Canvas size doesn't match video
**Fix:** Ensure canvas.width === video.videoWidth
