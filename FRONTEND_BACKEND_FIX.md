# Frontend-Backend Image Transfer Fix

## 🔍 Problem Analysis

Your frontend is sending images as **Blob objects** via FormData, but the backend is returning 500 errors with NO terminal output, which means the request isn't reaching the Flask endpoint.

### Current Flow:
1. Camera captures frame → `canvas.toBlob()` → **Blob object**
2. `attendanceAPI.recognize(blob, sessionId)` → **FormData with Blob**
3. Backend receives request → **500 ERROR (silently)**

### Root Cause:
The issue is likely that:
1. The Blob is being sent without a proper filename
2. The backend expects a specific format
3. Or there's a CORS/authentication issue preventing the request from reaching Flask

## ✅ Solution: Multiple Approaches

### Approach 1: Send as Base64 (Recommended)

This is the most reliable method for web applications.

#### Update `frontend/src/lib/api.ts`:

```typescript
// Attendance API
export const attendanceAPI = {
  // ... other methods ...
  
  recognize: async (image: Blob | string, sessionId: string) => {
    const formData = new FormData();
    
    if (typeof image === 'string') {
      // Already base64
      formData.append('image', image);
    } else {
      // Convert Blob to base64
      const base64 = await blobToBase64(image);
      formData.append('image', base64);
    }
    
    formData.append('session_id', sessionId);
    
    return api.post('/api/attendance/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // ... other methods ...
};

// Helper function to convert Blob to base64
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      resolve(base64); // Includes data:image/jpeg;base64, prefix
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
```

### Approach 2: Send Blob with Proper Filename

If you prefer to keep using Blobs:

```typescript
recognize: (image: Blob | string, sessionId: string) => {
  const formData = new FormData();
  
  if (typeof image === 'string') {
    formData.append('image', image);
  } else {
    // Add Blob with filename
    formData.append('image', image, 'capture.jpg');
  }
  
  formData.append('session_id', sessionId);
  
  return api.post('/api/attendance/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
},
```

### Approach 3: Send as JSON with Base64

Most reliable for debugging:

```typescript
recognize: async (image: Blob | string, sessionId: string) => {
  let base64Image: string;
  
  if (typeof image === 'string') {
    base64Image = image;
  } else {
    base64Image = await blobToBase64(image);
  }
  
  return api.post('/api/attendance/recognize', {
    image: base64Image,
    session_id: sessionId
  }, {
    headers: { 'Content-Type': 'application/json' },
  });
},
```

## 🔧 Complete Fixed Implementation

### 1. Update `frontend/src/lib/api.ts`:

```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Helper: Convert Blob to base64
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

// Attendance API
export const attendanceAPI = {
  startSession: (data: any) =>
    api.post('/api/attendance/start-session', data),
  
  endSession: (sessionId: string) =>
    api.post('/api/attendance/end-session', { session_id: sessionId }),
  
  recognize: async (image: Blob | string, sessionId: string) => {
    console.log('🔍 Sending recognition request...');
    console.log('Session ID:', sessionId);
    console.log('Image type:', typeof image);
    
    try {
      let base64Image: string;
      
      if (typeof image === 'string') {
        base64Image = image;
      } else {
        console.log('Converting Blob to base64...');
        base64Image = await blobToBase64(image);
        console.log('Base64 length:', base64Image.length);
      }
      
      const formData = new FormData();
      formData.append('image', base64Image);
      formData.append('session_id', sessionId);
      
      console.log('Sending FormData...');
      
      const response = await api.post('/api/attendance/recognize', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      console.log('✅ Response:', response.data);
      return response;
      
    } catch (error: any) {
      console.error('❌ Recognition error:', error);
      console.error('Response data:', error.response?.data);
      console.error('Response status:', error.response?.status);
      throw error;
    }
  },
  
  getSessionAttendance: (sessionId: string) =>
    api.get(`/api/attendance/session/${sessionId}`),
  
  getStudentAttendance: (studentId: string) =>
    api.get(`/api/attendance/student/${studentId}`),
  
  getSessions: () =>
    api.get('/api/attendance/sessions'),
};

// ... rest of your API exports ...
```

### 2. Update `frontend/src/components/CameraPreview.tsx`:

Add better error handling and logging:

```typescript
const captureFrame = () => {
  if (!videoRef.current || !canvasRef.current) return;
  
  const video = videoRef.current;
  const canvas = canvasRef.current;
  const context = canvas.getContext('2d');
  
  if (!context) return;
  
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0);
  
  canvas.toBlob((blob) => {
    if (blob && onCapture) {
      console.log('📸 Frame captured:', {
        size: blob.size,
        type: blob.type
      });
      onCapture(blob);
    } else {
      console.error('❌ Failed to create blob from canvas');
    }
  }, 'image/jpeg', 0.95);
};
```

### 3. Update `frontend/src/pages/AttendanceSession.tsx`:

Add comprehensive error handling:

```typescript
const handleCapture = async (blob: Blob) => {
  if (processing || !sessionId) return;
  
  console.log('🎯 handleCapture called', {
    blobSize: blob.size,
    blobType: blob.type,
    sessionId
  });
  
  setProcessing(true);
  
  try {
    console.log('Calling attendanceAPI.recognize...');
    const response = await attendanceAPI.recognize(blob, sessionId);
    const result = response.data;
    
    console.log('Recognition result:', result);
    setLastResult(result);
    
    if (result.status === 'recognized') {
      toast.success(`✓ ${result.student_name} - Attendance recorded`);
      loadSessionData();
    } else if (result.status === 'already_marked') {
      toast(`ℹ️ ${result.message}`, { icon: '🔵' });
    } else if (result.status === 'unknown') {
      toast.error('❌ Unknown student');
    } else if (result.status === 'no_face') {
      toast('⚠️ No face detected - Please face the camera', { 
        icon: '👤',
        duration: 2000 
      });
    } else if (result.error) {
      toast.error(result.error);
    }
  } catch (error: any) {
    console.error('❌ Recognition error:', error);
    console.error('Error response:', error.response);
    
    if (error.response?.data?.message) {
      toast.error(error.response.data.message);
    } else {
      toast.error('Recognition failed - Check console for details');
    }
  } finally {
    setProcessing(false);
  }
};
```

## 🐛 Debugging Steps

### Step 1: Check Browser Console

Open browser DevTools (F12) and look for:
- `🔍 Sending recognition request...`
- `Converting Blob to base64...`
- `Base64 length: XXXXX`
- Any error messages

### Step 2: Check Network Tab

In DevTools → Network tab:
1. Filter by "recognize"
2. Click on the request
3. Check:
   - **Request Headers**: Should have `Authorization: Bearer ...`
   - **Request Payload**: Should show FormData with image and session_id
   - **Response**: Check status code and response body

### Step 3: Check Backend Terminal

After making the request, your backend terminal should show:
```
================================================================================
RECOGNIZE FACE REQUEST
================================================================================
Method: POST
Content-Type: multipart/form-data
✓ Image from form data (base64)
✓ Session ID: ...
```

If you see NOTHING, the request isn't reaching the backend.

### Step 4: Test with Simple Endpoint

Add this to your frontend to test connectivity:

```typescript
// Test endpoint
const testBackend = async () => {
  try {
    const response = await api.get('/health');
    console.log('✅ Backend is reachable:', response.data);
  } catch (error) {
    console.error('❌ Backend not reachable:', error);
  }
};

// Call this on component mount
useEffect(() => {
  testBackend();
}, []);
```

## 🚨 Common Mistakes

### ❌ Mistake 1: Sending Raw Blob Without Filename

```typescript
// WRONG
formData.append('image', blob);
```

```typescript
// CORRECT
formData.append('image', blob, 'capture.jpg');
// OR convert to base64
```

### ❌ Mistake 2: Missing Data URL Prefix

```typescript
// WRONG - Just base64 string
formData.append('image', 'iVBORw0KGgoAAAANS...');
```

```typescript
// CORRECT - With data URL prefix
formData.append('image', 'data:image/jpeg;base64,iVBORw0KGgoAAAANS...');
```

### ❌ Mistake 3: Wrong Content-Type

```typescript
// WRONG
headers: { 'Content-Type': 'application/json' }
```

```typescript
// CORRECT for FormData
headers: { 'Content-Type': 'multipart/form-data' }
```

### ❌ Mistake 4: Not Awaiting Blob Conversion

```typescript
// WRONG
const base64 = blobToBase64(blob); // Returns Promise!
formData.append('image', base64);
```

```typescript
// CORRECT
const base64 = await blobToBase64(blob);
formData.append('image', base64);
```

## ✅ Verification Checklist

After implementing the fix:

- [ ] Browser console shows "🔍 Sending recognition request..."
- [ ] Browser console shows "Base64 length: XXXXX"
- [ ] Network tab shows 200 or 400 response (not 500)
- [ ] Backend terminal shows "RECOGNIZE FACE REQUEST"
- [ ] Backend terminal shows "✓ Image from form data (base64)"
- [ ] No CORS errors in browser console
- [ ] Authorization header is present in request

## 🎯 Expected Flow

1. **Camera captures** → Blob created
2. **Blob → Base64** → Data URL string
3. **FormData created** → image + session_id
4. **POST request** → With Authorization header
5. **Backend receives** → Logs appear in terminal
6. **Backend processes** → Face recognition
7. **Response returned** → 200 with result
8. **Frontend updates** → Shows result to user

## 📝 Summary

The key fix is to **convert Blob to base64** before sending, which ensures:
- ✅ Consistent format across browsers
- ✅ Easy debugging (can see the data)
- ✅ Backend can decode reliably
- ✅ No filename issues

Implement **Approach 1** (base64 conversion) for the most reliable solution!
