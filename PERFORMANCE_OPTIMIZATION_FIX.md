# Face Recognition Performance Optimization

## Issues Identified:
1. **Too frequent API calls** - Detection running every 2 seconds
2. **Heavy processing** - Full InsightFace detection on every frame
3. **No frame skipping** - Processing every frame even when face hasn't moved
4. **Large image processing** - Sending full resolution images to backend

## Solutions Applied:

### 1. Reduce Detection Frequency
- Change from 2 seconds to 3-4 seconds
- Skip frames when face is already detected and hasn't moved significantly

### 2. Optimize Image Processing
- Reduce image resolution before sending to backend
- Use lower quality JPEG compression
- Skip detection if no significant change in frame

### 3. Improve Backend Performance
- Cache face detector initialization
- Use smaller detection size
- Implement frame difference checking