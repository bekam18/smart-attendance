# Quick Debug Commands

## Copy-Paste These in Browser Console (F12)

### 1. Check if Canvas Exists and is Sized
```javascript
const canvas = document.querySelector('canvas');
console.log('✓ Canvas found:', !!canvas);
console.log('✓ Canvas size:', canvas?.width, 'x', canvas?.height);
console.log('✓ Canvas position:', canvas?.style.position);
console.log('✓ Canvas z-index:', canvas?.style.zIndex);
```

### 2. Draw Test Red Box (Should Show Immediately)
```javascript
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
ctx.strokeStyle = 'red';
ctx.lineWidth = 10;
ctx.strokeRect(50, 50, 300, 300);
console.log('✓ Red test box drawn - DO YOU SEE IT?');
```

### 3. Check Video Status
```javascript
const video = document.querySelector('video');
console.log('✓ Video ready:', video?.readyState === 4);
console.log('✓ Video size:', video?.videoWidth, 'x', video?.videoHeight);
console.log('✓ Video playing:', !video?.paused);
```

### 4. Force Canvas to Front (If Not Visible)
```javascript
const canvas = document.querySelector('canvas');
canvas.style.position = 'absolute';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.zIndex = '9999';
canvas.style.border = '3px solid yellow'; // Debug border
console.log('✓ Canvas forced to front with yellow border');
```

### 5. Simulate Face Box (Test Drawing Logic)
```javascript
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
const video = document.querySelector('video');

// Sync canvas size
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;

// Draw fake face box
const fakeBox = { x: 150, y: 100, w: 200, h: 250 };
ctx.clearRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = 'lime';
ctx.lineWidth = 3;
ctx.strokeRect(fakeBox.x, fakeBox.y, fakeBox.w, fakeBox.h);

console.log('✓ Fake lime box drawn at:', fakeBox);
console.log('DO YOU SEE A GREEN BOX?');
```

### 6. Check All Canvases (If Multiple)
```javascript
const canvases = document.querySelectorAll('canvas');
console.log('✓ Total canvases:', canvases.length);
canvases.forEach((c, i) => {
  console.log(`Canvas ${i}:`, {
    class: c.className,
    size: `${c.width}x${c.height}`,
    position: c.style.position,
    zIndex: c.style.zIndex
  });
});
```

### 7. Monitor Detection Responses
```javascript
// This will log all fetch responses
const originalFetch = window.fetch;
window.fetch = function(...args) {
  return originalFetch.apply(this, args).then(response => {
    if (args[0].includes('detect-face')) {
      response.clone().json().then(data => {
        console.log('🔍 DETECTION RESPONSE:', data);
      });
    }
    return response;
  });
};
console.log('✓ Monitoring detection responses...');
```

### 8. Continuous Test Box (Animated)
```javascript
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
let testX = 100;

const testInterval = setInterval(() => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = 'red';
  ctx.lineWidth = 5;
  ctx.strokeRect(testX, 100, 200, 200);
  testX = (testX + 5) % (canvas.width - 200);
}, 50);

console.log('✓ Animated red box started');
console.log('To stop: clearInterval(' + testInterval + ')');
```

## Interpretation

### If Red Test Box Shows
✅ Canvas rendering works
✅ Canvas is visible
✅ Problem is with detection or data

**Next:** Check console for "DRAW BOX:" messages

### If Red Test Box Doesn't Show
❌ Canvas not visible or not positioned correctly
❌ Canvas might be 0x0 size
❌ Canvas might be behind video

**Next:** Run command #4 to force canvas to front

### If Fake Lime Box Shows
✅ Drawing logic works
✅ Canvas positioned correctly
✅ Problem is backend not returning data

**Next:** Check Network tab for API responses

### If Nothing Shows At All
❌ Canvas element missing
❌ JavaScript error preventing execution
❌ Video not loaded

**Next:** Check console for errors, verify video is playing

## Quick Decision Tree

```
Start Camera
    ↓
Run Command #2 (Red Test Box)
    ↓
    ├─ RED BOX SHOWS
    │   ↓
    │   Check console for "DRAW BOX:" logs
    │   ↓
    │   ├─ LOGS PRESENT → Backend working, check coordinates
    │   └─ NO LOGS → Backend not returning data
    │
    └─ NO RED BOX
        ↓
        Run Command #4 (Force Canvas Front)
        ↓
        Run Command #2 Again
        ↓
        ├─ NOW SHOWS → CSS/positioning issue (fixed)
        └─ STILL NOTHING → Canvas not created or JS error
```

## Expected Console Output (When Working)

```
Video metadata loaded, starting face detection...
Canvas resized to: 640x480
Sending face detection request...
Face detection response: {status: 'success', faces: [...]}
Face detected at: {x: 120, y: 80, w: 200, h: 250}
DRAW BOX: x=120, y=80, w=200, h=250
DRAW BOX: x=121, y=81, w=200, h=250
DRAW BOX: x=122, y=82, w=200, h=250
...
```

## Common Results

| Symptom | Cause | Fix |
|---------|-------|-----|
| No red box | Canvas not visible | Command #4 |
| Red box but no green | Backend not working | Check Network tab |
| Green box wrong place | Coordinates wrong | Check backend response |
| Box appears then disappears | Detection failing | Check lighting/face position |
| Multiple canvases | Hidden canvas used | Check command #6 |

## Success Indicators

✅ Red test box visible
✅ Fake lime box visible
✅ Console shows "DRAW BOX:" messages
✅ Network shows successful API calls
✅ No JavaScript errors

If all above are true, the green box WILL show when face is detected!
