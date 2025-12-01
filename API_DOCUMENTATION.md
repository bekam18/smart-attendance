# API Documentation

Base URL: `http://localhost:5000`

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /api/auth/login
Login for all user roles.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "admin|instructor|student",
    "name": "string",
    "student_id": "string (if student)"
  }
}
```

#### POST /api/auth/register-student
Register a new student.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "name": "string",
  "student_id": "string",
  "department": "string (optional)",
  "year": "string (optional)"
}
```

**Response:**
```json
{
  "message": "Student registered successfully",
  "student_id": "string"
}
```

#### GET /api/auth/me
Get current user information.

**Headers:** Authorization required

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "string",
  "name": "string"
}
```

### Admin

#### POST /api/admin/add-instructor
Add a new instructor (Admin only).

**Headers:** Authorization required

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "name": "string",
  "department": "string (optional)"
}
```

**Response:**
```json
{
  "message": "Instructor added successfully",
  "instructor_id": "string"
}
```

#### GET /api/admin/instructors
Get all instructors (Admin only).

**Headers:** Authorization required

**Response:**
```json
[
  {
    "id": "string",
    "username": "string",
    "name": "string",
    "email": "string",
    "department": "string",
    "created_at": "ISO 8601 date"
  }
]
```

#### GET /api/admin/students
Get all students (Admin/Instructor).

**Headers:** Authorization required

**Response:**
```json
[
  {
    "id": "string",
    "student_id": "string",
    "name": "string",
    "email": "string",
    "department": "string",
    "year": "string",
    "face_registered": boolean,
    "created_at": "ISO 8601 date"
  }
]
```

#### GET /api/admin/attendance/all
Get all attendance records (Admin only).

**Headers:** Authorization required

**Query Parameters:**
- `start_date` (optional): Filter by start date (YYYY-MM-DD)
- `end_date` (optional): Filter by end date (YYYY-MM-DD)
- `student_id` (optional): Filter by student ID

**Response:**
```json
[
  {
    "id": "string",
    "student_id": "string",
    "student_name": "string",
    "session_id": "string",
    "timestamp": "ISO 8601 date",
    "date": "YYYY-MM-DD",
    "confidence": number,
    "status": "present"
  }
]
```

#### POST /api/admin/upload-model
Upload model files (Admin only).

**Headers:** Authorization required, Content-Type: multipart/form-data

**Form Data:**
- `file`: File (required)
- `type`: "classifier" | "encoder" | "classes"

**Response:**
```json
{
  "message": "Model file uploaded successfully",
  "filename": "string"
}
```

#### GET /api/admin/stats
Get system statistics (Admin only).

**Headers:** Authorization required

**Response:**
```json
{
  "total_students": number,
  "total_instructors": number,
  "total_attendance_records": number,
  "active_sessions": number,
  "students_with_face": number
}
```

### Students

#### GET /api/students/profile
Get student profile (Student only).

**Headers:** Authorization required

**Response:**
```json
{
  "id": "string",
  "student_id": "string",
  "name": "string",
  "email": "string",
  "department": "string",
  "year": "string",
  "face_registered": boolean
}
```

#### POST /api/students/register-face
Register face images (Student only).

**Headers:** Authorization required, Content-Type: multipart/form-data

**Form Data:**
- `images`: File[] (multiple images)

**Response:**
```json
{
  "message": "Face images registered successfully",
  "images_count": number
}
```

#### GET /api/students/attendance
Get student's attendance history (Student only).

**Headers:** Authorization required

**Response:**
```json
[
  {
    "id": "string",
    "date": "YYYY-MM-DD",
    "timestamp": "ISO 8601 date",
    "session_name": "string",
    "confidence": number,
    "status": "present"
  }
]
```

### Attendance

#### POST /api/attendance/start-session
Start a new attendance session (Instructor only).

**Headers:** Authorization required

**Request Body:**
```json
{
  "name": "string",
  "course": "string (optional)"
}
```

**Response:**
```json
{
  "message": "Session started successfully",
  "session_id": "string",
  "session": {
    "id": "string",
    "name": "string",
    "start_time": "ISO 8601 date"
  }
}
```

#### POST /api/attendance/end-session
End an attendance session (Instructor only).

**Headers:** Authorization required

**Request Body:**
```json
{
  "session_id": "string"
}
```

**Response:**
```json
{
  "message": "Session ended successfully"
}
```

#### POST /api/attendance/recognize
Recognize face and record attendance (Instructor only).

**Headers:** Authorization required, Content-Type: multipart/form-data

**Form Data:**
- `image`: File or base64 string (required)
- `session_id`: string (required)

**Response:**
```json
{
  "status": "recognized|unknown|no_face|already_marked|error",
  "student_id": "string (if recognized)",
  "student_name": "string (if recognized)",
  "confidence": number,
  "message": "string"
}
```

**Status Codes:**
- `recognized`: Face recognized and attendance recorded
- `unknown`: Face detected but not recognized
- `no_face`: No face detected in image
- `already_marked`: Student already marked present in this session
- `error`: Error occurred during recognition

#### GET /api/attendance/session/:sessionId
Get attendance for a specific session (Instructor/Admin).

**Headers:** Authorization required

**Response:**
```json
{
  "session": {
    "id": "string",
    "name": "string",
    "start_time": "ISO 8601 date",
    "status": "active|completed",
    "attendance_count": number
  },
  "attendance": [
    {
      "student_id": "string",
      "student_name": "string",
      "timestamp": "ISO 8601 date",
      "confidence": number
    }
  ]
}
```

#### GET /api/attendance/student/:studentId
Get attendance records for a specific student.

**Headers:** Authorization required

**Response:**
```json
{
  "student": {
    "student_id": "string",
    "name": "string"
  },
  "attendance": [
    {
      "id": "string",
      "date": "YYYY-MM-DD",
      "timestamp": "ISO 8601 date",
      "session_name": "string",
      "confidence": number
    }
  ]
}
```

#### GET /api/attendance/sessions
Get all sessions (Instructor/Admin).

**Headers:** Authorization required

**Response:**
```json
[
  {
    "id": "string",
    "name": "string",
    "instructor_name": "string",
    "course": "string",
    "start_time": "ISO 8601 date",
    "end_time": "ISO 8601 date or null",
    "status": "active|completed",
    "attendance_count": number
  }
]
```

### Debug

#### GET /api/debug/echo
Test endpoint.

**Response:**
```json
{
  "message": "SmartAttendance API is running",
  "method": "GET",
  "timestamp": "ISO 8601 date"
}
```

#### POST /api/debug/recognition-test
Test face recognition without recording attendance.

**Headers:** Content-Type: multipart/form-data

**Form Data:**
- `image`: File (required)

**Response:**
```json
{
  "test_mode": true,
  "result": {
    "status": "string",
    "student_id": "string (if recognized)",
    "confidence": number
  }
}
```

#### GET /api/debug/model-status
Check model loading status.

**Response:**
```json
{
  "model_loaded": boolean,
  "model_path": "string",
  "files": {
    "classifier": boolean,
    "label_encoder": boolean,
    "label_classes": boolean
  },
  "threshold": number
}
```

#### POST /api/debug/reload-models
Force reload models.

**Response:**
```json
{
  "success": boolean,
  "model_loaded": boolean
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting in production.

## CORS

CORS is enabled for origins specified in the backend configuration. Default:
- http://localhost:5173
- http://localhost:3000

## WebSocket Support

Currently not implemented. Future versions may include WebSocket support for real-time attendance updates.
