# Testing Guide

Comprehensive testing guide for SmartAttendance system.

## Manual Testing

### 1. Authentication Testing

#### Test Login (All Roles)
```bash
# Admin Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Instructor Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"instructor","password":"inst123"}'

# Student Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"stud123"}'
```

Expected: Returns JWT token and user info

#### Test Invalid Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid","password":"wrong"}'
```

Expected: 401 error with "Invalid credentials"

### 2. Admin Functionality Testing

#### Get System Stats
```bash
TOKEN="your-admin-token"

curl -X GET http://localhost:5000/api/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Returns system statistics

#### Add Instructor
```bash
curl -X POST http://localhost:5000/api/admin/add-instructor \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newinstructor",
    "password":"pass123",
    "email":"new@example.com",
    "name":"New Instructor",
    "department":"CS"
  }'
```

Expected: 201 with instructor ID

#### Get All Students
```bash
curl -X GET http://localhost:5000/api/admin/students \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Array of student objects

### 3. Instructor Functionality Testing

#### Start Attendance Session
```bash
TOKEN="your-instructor-token"

curl -X POST http://localhost:5000/api/attendance/start-session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Morning Lecture",
    "course":"CS101"
  }'
```

Expected: Returns session ID

#### Test Face Recognition
```bash
SESSION_ID="your-session-id"

curl -X POST http://localhost:5000/api/attendance/recognize \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test_face.jpg" \
  -F "session_id=$SESSION_ID"
```

Expected: Recognition result with status

#### End Session
```bash
curl -X POST http://localhost:5000/api/attendance/end-session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"'$SESSION_ID'"}'
```

Expected: Success message

### 4. Student Functionality Testing

#### Get Student Profile
```bash
TOKEN="your-student-token"

curl -X GET http://localhost:5000/api/students/profile \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Student profile data

#### Register Face Images
```bash
curl -X POST http://localhost:5000/api/students/register-face \
  -H "Authorization: Bearer $TOKEN" \
  -F "images=@face1.jpg" \
  -F "images=@face2.jpg" \
  -F "images=@face3.jpg"
```

Expected: Success with image count

#### Get Attendance History
```bash
curl -X GET http://localhost:5000/api/students/attendance \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Array of attendance records

### 5. Debug Endpoint Testing

#### Check Model Status
```bash
curl -X GET http://localhost:5000/api/debug/model-status
```

Expected: Model loading status and file existence

#### Test Recognition (No Auth Required)
```bash
curl -X POST http://localhost:5000/api/debug/recognition-test \
  -F "image=@test_face.jpg"
```

Expected: Recognition result in test mode

#### Reload Models
```bash
curl -X POST http://localhost:5000/api/debug/reload-models
```

Expected: Success status

## Frontend Testing

### 1. Login Flow
1. Navigate to http://localhost:5173
2. Enter credentials: `admin` / `admin123`
3. Click Login
4. Verify redirect to admin dashboard

### 2. Admin Dashboard
1. Login as admin
2. Verify statistics display
3. Click "Add Instructor"
4. Fill form and submit
5. Verify instructor appears in list
6. Check students table
7. Verify face registration status

### 3. Instructor Dashboard
1. Login as instructor
2. Click "Start New Session"
3. Enter session details
4. Click "Create & Start"
5. Verify redirect to session page
6. Click "Start Camera"
7. Grant camera permissions
8. Verify live feed appears
9. Verify auto-capture is working
10. Check attendance list updates
11. Click "End Session"
12. Verify session status changes

### 4. Student Dashboard
1. Login as student
2. Verify profile information
3. Check attendance statistics
4. View attendance history table
5. If face not registered:
   - Click "Register Face"
   - Start camera
   - Capture multiple images
   - Submit registration
   - Verify success message

### 5. Camera Functionality
1. Test in different browsers (Chrome, Firefox, Safari)
2. Verify camera permissions prompt
3. Test start/stop camera
4. Test manual capture
5. Test auto-capture
6. Verify image quality

### 6. Responsive Design
1. Test on desktop (1920x1080)
2. Test on tablet (768x1024)
3. Test on mobile (375x667)
4. Verify all elements are accessible
5. Check navigation works on all sizes

## Integration Testing

### Complete Attendance Flow
1. Admin creates instructor account
2. Instructor logs in
3. Instructor starts session
4. Student registers face (if needed)
5. Instructor captures student face
6. System recognizes student
7. Attendance is recorded
8. Student views attendance
9. Admin views all attendance
10. Instructor ends session

### Error Handling
1. Test with no internet connection
2. Test with invalid tokens
3. Test with expired tokens
4. Test with missing model files
5. Test with invalid image formats
6. Test with no face in image
7. Test duplicate attendance
8. Test concurrent sessions

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test login endpoint
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:5000/api/auth/login

# Test recognition endpoint
ab -n 100 -c 5 -p image.jpg -T multipart/form-data \
  http://localhost:5000/api/debug/recognition-test
```

### Metrics to Monitor
- Response time (should be < 2s for recognition)
- Memory usage (should be stable)
- CPU usage (should not spike excessively)
- Database query time
- Image processing time

## Security Testing

### 1. Authentication Bypass
```bash
# Try accessing protected endpoint without token
curl -X GET http://localhost:5000/api/admin/stats

# Expected: 401 Unauthorized
```

### 2. Role Escalation
```bash
# Try accessing admin endpoint with student token
curl -X GET http://localhost:5000/api/admin/stats \
  -H "Authorization: Bearer $STUDENT_TOKEN"

# Expected: 403 Forbidden
```

### 3. SQL Injection (MongoDB)
```bash
# Try injection in login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":{"$ne":null},"password":{"$ne":null}}'

# Expected: Should fail, not bypass authentication
```

### 4. XSS Testing
1. Try entering `<script>alert('XSS')</script>` in forms
2. Verify it's escaped in output
3. Check all user input fields

### 5. CSRF Testing
1. Verify CORS is properly configured
2. Test cross-origin requests
3. Verify token validation

## Automated Testing

### Backend Unit Tests (Example)

Create `backend/tests/test_auth.py`:
```python
import pytest
from app import create_app
from db.mongo import get_db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid(client):
    response = client.post('/api/auth/login', json={
        'username': 'invalid',
        'password': 'wrong'
    })
    assert response.status_code == 401
```

Run tests:
```bash
cd backend
pytest tests/
```

### Frontend Unit Tests (Example)

Create `frontend/src/lib/__tests__/auth.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { setAuth, getStoredUser, clearAuth } from '../auth';

describe('Auth utilities', () => {
  it('should store and retrieve user', () => {
    const user = {
      id: '1',
      username: 'test',
      email: 'test@test.com',
      role: 'student',
      name: 'Test User'
    };
    
    setAuth('token123', user);
    const stored = getStoredUser();
    
    expect(stored).toEqual(user);
  });
  
  it('should clear auth data', () => {
    clearAuth();
    const stored = getStoredUser();
    
    expect(stored).toBeNull();
  });
});
```

Run tests:
```bash
cd frontend
npm test
```

## Test Checklist

### Pre-Deployment Testing

- [ ] All API endpoints return correct responses
- [ ] Authentication works for all roles
- [ ] Authorization prevents unauthorized access
- [ ] Face recognition works with test images
- [ ] Camera access works in all browsers
- [ ] Responsive design works on all devices
- [ ] Forms validate input correctly
- [ ] Error messages are user-friendly
- [ ] Loading states are shown
- [ ] Success messages are displayed
- [ ] Database operations are atomic
- [ ] File uploads work correctly
- [ ] Image processing is accurate
- [ ] Session management works
- [ ] Logout clears all data
- [ ] Password hashing is secure
- [ ] JWT tokens expire correctly
- [ ] CORS is configured properly
- [ ] Environment variables are set
- [ ] Model files are loaded
- [ ] Database indexes are created

### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

### Device Testing

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)
- [ ] Mobile (414x896)

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm test
```

## Test Data

### Sample Users
- Admin: `admin` / `admin123`
- Instructor: `instructor` / `inst123`
- Student: `student` / `stud123`

### Sample Images
Place test face images in `backend/tests/fixtures/`:
- `face_frontal.jpg` - Front-facing face
- `face_left.jpg` - Left profile
- `face_right.jpg` - Right profile
- `no_face.jpg` - Image without face
- `multiple_faces.jpg` - Multiple faces

## Reporting Issues

When reporting bugs, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Screenshots/logs
5. Environment details
6. Browser/device info

## Test Coverage Goals

- Backend: > 80% code coverage
- Frontend: > 70% code coverage
- Critical paths: 100% coverage
- API endpoints: 100% coverage
