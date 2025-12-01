# Emergency Debug - Box Not Showing

## Quick Diagnosis (Copy-Paste in Browser Console)

### Step 1: Check if Canvas Exists
```javascript
const canvas = document.querySelector('canvas');
console.log('Canvas found:', !!canvas);
console.log('Canvas size:', canvas?.width, 'x', canvas?.height);
```

### Step 2: Draw Test Box (Should Show Immediately)
```javascript
const canvas = document.querySelector('canvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  ctx.strokeStyle = 'red';
  ctx.lineWidth = 10;
  ctx.strokeRect(50, 50, 300, 300);
  console.log('✓ RED BOX DRAWN - DO YOU SEE IT?');
}
```

### Step 3: Check Video Status
```javascript
const video = document.querySelector('video');
console.log('Video ready:', video?.readyState);
console.log('Video size:', video?.videoWidth, 'x', video?.videoHeight);
```

### Step 4: Check Detection Logs
Look in console for:
- "Video metadata loaded"
- "Sending face detection request"
- "Face detection response"
- "DRAW BOX:"

### Step 5: Force Canvas Visible
```javascript
const canvas = document.querySelector('canvas');
canvas.style.position = 'absolute';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.zIndex = '9999';
canvas.style.border = '5px solid yellow';
console.log('✓ Canvas forced to front');
```

### Step 6: Check Network Requests
1. Open Network tab in DevTools
2. Filter by "detect-face"
3. Check if requests are being sent
4. Check response data

## What to Report

Please tell me:
1. Do you see the RED test box? (Yes/No)
2. What logs appear in console?
3. Are there any errors in console?
4. Do you see "detect-face" requests in Network tab?

## Quick Fixes

### If RED box shows but no blue box:
**Problem:** Backend not returning data
**Fix:** Check Network tab for API responses

### If NO red box shows:
**Problem:** Canvas not visible
**Fix:** Run Step 5 above

### If errors in console:
**Problem:** JavaScript error
**Fix:** Share the error message
