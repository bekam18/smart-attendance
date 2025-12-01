# 🚀 Quick Fix Reference - CORS & JWT

## 🎯 The 4 Critical Fixes

### 1️⃣ CORS: Add `automatic_options=True`

**File**: `backend/app.py`

```python
CORS(app, automatic_options=True, ...)
```

**Why**: Prevents OPTIONS requests from reaching route handlers.

---

### 2️⃣ JWT: Correct Decorator Order

**File**: `backend/blueprints/attendance.py`

```python
# ✅ CORRECT
@jwt_required()              # First: Verify JWT
@role_required('instructor')  # Second: Check role
def my_route():
    pass

# ❌ WRONG
@role_required('instructor')  # Would run before JWT verification
@jwt_required()
def my_route():
    pass
```

**Why**: Flask decorators execute bottom-to-top.

---

### 3️⃣ Security: Simplify role_required

**File**: `backend/utils/security.py`

```python
def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # JWT already verified by @jwt_required()
            user_id = get_jwt_identity()  # Safe to call now
            # ... check role ...
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

**Why**: No need to manually verify JWT - `@jwt_required()` does it.

---

### 4️⃣ Frontend: Delete Content-Type for FormData

**File**: `frontend/src/lib/api.ts`

```typescript
api.interceptors.request.use((config) => {
  // Delete Content-Type for FormData to let axios set boundary
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});
```

**Why**: Axios needs to set `multipart/form-data; boundary=...` automatically.

---

## 🔍 Quick Diagnosis

### Problem: OPTIONS hitting backend

**Symptom**: Backend logs show `Method: OPTIONS`

**Fix**: Add `automatic_options=True` to CORS config

---

### Problem: RuntimeError about jwt_required

**Symptom**: `RuntimeError: You must call @jwt_required() before using this method`

**Fix**: Put `@jwt_required()` BELOW `@role_required()` (so it executes first)

---

### Problem: No image data in request

**Symptom**: Backend logs show `Files keys: []`

**Fix**: Delete Content-Type header for FormData in axios interceptor

---

## ✅ Verification Checklist

- [ ] Backend logs show `Method: POST` (not OPTIONS)
- [ ] Backend logs show `Files keys: ['image']`
- [ ] Backend logs show `✓ Image from file upload: X bytes`
- [ ] Browser console shows `File created: capture.jpg`
- [ ] Browser Network tab shows OPTIONS returns 200 OK
- [ ] Browser Network tab shows POST returns 200 OK
- [ ] Face recognition works without errors

---

## 🎯 Expected Flow

```
1. Browser → OPTIONS /api/attendance/recognize
   ↓
2. Flask-CORS intercepts (automatic_options=True)
   ↓
3. Flask-CORS returns 200 OK with CORS headers
   ↓
4. Browser → POST /api/attendance/recognize
   ↓
5. @jwt_required() verifies JWT token
   ↓
6. @role_required() checks user role
   ↓
7. recognize_face() processes image
   ↓
8. Backend returns recognition result
```

---

## 📝 Quick Test

```bash
# Run test script
test_cors_jwt_fix.bat

# Start backend
cd backend && python app.py

# Start frontend
cd frontend && npm run dev

# Test in browser
# 1. Login as instructor
# 2. Start session
# 3. Capture face
# 4. Check logs
```

---

## 🆘 Still Having Issues?

1. Check `CORS_JWT_FIX_COMPLETE.md` for detailed explanation
2. Check `FIXES_APPLIED_SUMMARY.md` for all code changes
3. Check `TROUBLESHOOTING.md` for common problems
4. Verify all 4 fixes are applied correctly
5. Restart both backend and frontend servers

---

## 🎉 Success Indicators

✅ No OPTIONS in backend logs  
✅ POST requests show image data  
✅ No RuntimeError exceptions  
✅ Face recognition works  
✅ Attendance recorded successfully  

**System is working!** 🚀
