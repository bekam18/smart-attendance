# 🔄 CORS & JWT Fix Flow Diagram

## 📊 Before Fix (Broken)

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  User clicks "Capture" → FormData created                       │
│  axios.post('/api/attendance/recognize', formData)              │
│                                                                  │
│  Headers:                                                        │
│    Content-Type: application/json  ← WRONG!                     │
│    Authorization: Bearer <token>                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1. OPTIONS (preflight)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND                               │
│                                                                  │
│  Flask-CORS (automatic_options=False)                           │
│    → Does NOT intercept OPTIONS                                 │
│    → Routes OPTIONS to endpoint                                 │
│                                                                  │
│  @attendance_bp.route('/recognize', methods=['POST'])           │
│  @role_required('instructor')  ← Executes SECOND                │
│  @jwt_required()               ← Executes FIRST                 │
│  def recognize_face():                                          │
│      user_id = get_jwt_identity()  ← RuntimeError!              │
│                                                                  │
│  Result: 400 Bad Request or RuntimeError                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 2. Error response
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  ❌ Error: Request failed with status code 400                  │
│  ❌ No image data found                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ After Fix (Working)

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  User clicks "Capture" → FormData created                       │
│  axios.post('/api/attendance/recognize', formData)              │
│                                                                  │
│  Interceptor detects FormData:                                  │
│    → Deletes Content-Type header                                │
│    → Axios sets: multipart/form-data; boundary=...              │
│                                                                  │
│  Headers:                                                        │
│    Content-Type: multipart/form-data; boundary=...  ← CORRECT!  │
│    Authorization: Bearer <token>                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1. OPTIONS (preflight)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND                               │
│                                                                  │
│  Flask-CORS (automatic_options=True)  ← FIX #1                  │
│    → Intercepts OPTIONS automatically                           │
│    → Returns 200 OK with CORS headers                           │
│    → Never reaches route handler                                │
│                                                                  │
│  ✅ OPTIONS handled by Flask-CORS                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 2. 200 OK (CORS headers)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  ✅ OPTIONS successful                                          │
│  → Sends actual POST request                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 3. POST (actual request)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND                               │
│                                                                  │
│  @attendance_bp.route('/recognize', methods=['POST'])           │
│  @jwt_required()               ← Executes FIRST  ← FIX #2       │
│  @role_required('instructor')  ← Executes SECOND                │
│  def recognize_face():                                          │
│                                                                  │
│  Execution flow:                                                │
│  1. @jwt_required() verifies JWT token ✅                       │
│  2. @role_required() checks user role ✅                        │
│  3. recognize_face() processes request ✅                       │
│                                                                  │
│  Request parsing:                                               │
│    Content-Type: multipart/form-data; boundary=...              │
│    → Flask parses FormData correctly                            │
│    → request.files['image'] = <FileStorage>  ✅                 │
│    → request.form['session_id'] = "..."  ✅                     │
│                                                                  │
│  Face recognition:                                              │
│    → Decode image ✅                                            │
│    → Detect face ✅                                             │
│    → Extract embeddings ✅                                      │
│    → Classify student ✅                                        │
│    → Record attendance ✅                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 4. Success response
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  ✅ Response: {                                                 │
│      status: "recognized",                                      │
│      student_id: "S001",                                        │
│      student_name: "John Doe",                                  │
│      confidence: 0.9850                                         │
│    }                                                            │
│                                                                  │
│  → Display success message                                      │
│  → Update attendance list                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Decorator Execution Order

### ❌ WRONG Order (Before Fix)

```python
@attendance_bp.route('/recognize', methods=['POST'])
@role_required('instructor')  # Decorator 2
@jwt_required()               # Decorator 1
def recognize_face():         # Original function
    pass

# Execution order (bottom-to-top):
# 1. recognize_face is wrapped by jwt_required → jwt_required(recognize_face)
# 2. Result is wrapped by role_required → role_required(jwt_required(recognize_face))

# When request arrives:
# 1. role_required wrapper runs FIRST
#    → Calls get_jwt_identity()
#    → RuntimeError! JWT not verified yet
# 2. jwt_required wrapper would run SECOND (but never reached)
# 3. recognize_face would run THIRD (but never reached)
```

### ✅ CORRECT Order (After Fix)

```python
@attendance_bp.route('/recognize', methods=['POST'])
@jwt_required()               # Decorator 2
@role_required('instructor')  # Decorator 1
def recognize_face():         # Original function
    pass

# Execution order (bottom-to-top):
# 1. recognize_face is wrapped by role_required → role_required(recognize_face)
# 2. Result is wrapped by jwt_required → jwt_required(role_required(recognize_face))

# When request arrives:
# 1. jwt_required wrapper runs FIRST
#    → Verifies JWT token ✅
#    → Stores identity in context
# 2. role_required wrapper runs SECOND
#    → Calls get_jwt_identity() ✅ (works now!)
#    → Checks user role
# 3. recognize_face runs THIRD
#    → Processes the request
```

---

## 🌐 CORS Flow

### ❌ Without automatic_options=True

```
Browser                    Flask-CORS              Flask Route
  │                           │                        │
  │ OPTIONS request           │                        │
  ├──────────────────────────>│                        │
  │                           │ No interception        │
  │                           │ (automatic_options=    │
  │                           │  False)                │
  │                           │                        │
  │                           │ Routes to endpoint     │
  │                           ├───────────────────────>│
  │                           │                        │
  │                           │                        │ @jwt_required()
  │                           │                        │ tries to verify
  │                           │                        │ JWT on OPTIONS
  │                           │                        │
  │                           │                        │ ❌ Fails!
  │                           │<───────────────────────┤
  │                           │                        │
  │ 400 Bad Request           │                        │
  │<──────────────────────────┤                        │
  │                           │                        │
  │ ❌ CORS error             │                        │
  │ POST blocked              │                        │
```

### ✅ With automatic_options=True

```
Browser                    Flask-CORS              Flask Route
  │                           │                        │
  │ OPTIONS request           │                        │
  ├──────────────────────────>│                        │
  │                           │                        │
  │                           │ Intercepts OPTIONS     │
  │                           │ (automatic_options=    │
  │                           │  True)                 │
  │                           │                        │
  │                           │ Adds CORS headers      │
  │                           │ Returns 200 OK         │
  │                           │                        │
  │ 200 OK + CORS headers     │                        │
  │<──────────────────────────┤                        │
  │                           │                        │
  │ ✅ Preflight success      │                        │
  │                           │                        │
  │ POST request              │                        │
  ├──────────────────────────>│                        │
  │                           │ Passes through         │
  │                           ├───────────────────────>│
  │                           │                        │
  │                           │                        │ @jwt_required()
  │                           │                        │ verifies JWT ✅
  │                           │                        │
  │                           │                        │ @role_required()
  │                           │                        │ checks role ✅
  │                           │                        │
  │                           │                        │ recognize_face()
  │                           │                        │ processes ✅
  │                           │                        │
  │                           │<───────────────────────┤
  │                           │                        │
  │ 200 OK + result           │                        │
  │<──────────────────────────┤                        │
  │                           │                        │
  │ ✅ Success!               │                        │
```

---

## 📦 FormData Content-Type

### ❌ Wrong (Before Fix)

```
Frontend Axios Config:
  headers: {
    'Content-Type': 'application/json'  ← Set globally
  }

When sending FormData:
  Content-Type: application/json  ← WRONG! No boundary!

Backend receives:
  request.content_type = 'application/json'
  request.files = {}  ← Empty!
  request.form = {}   ← Empty!
  request.json = None ← Can't parse as JSON!

Result: ❌ No image data
```

### ✅ Correct (After Fix)

```
Frontend Axios Interceptor:
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];  ← Let axios set it
  }

When sending FormData:
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
                                     ↑
                                     Critical for parsing!

Backend receives:
  request.content_type = 'multipart/form-data; boundary=...'
  request.files = {'image': <FileStorage>}  ← ✅ Has image!
  request.form = {'session_id': '...'}      ← ✅ Has session_id!

Result: ✅ Image data received correctly
```

---

## 🎯 Summary

| Issue | Root Cause | Fix | Result |
|-------|------------|-----|--------|
| OPTIONS hitting backend | `automatic_options=False` | Set to `True` | OPTIONS handled by Flask-CORS |
| RuntimeError | Wrong decorator order | Swap decorators | JWT verified before role check |
| No image data | Wrong Content-Type | Delete header for FormData | Proper multipart/form-data |

**All issues fixed! System working! 🚀**
