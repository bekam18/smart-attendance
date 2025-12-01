# Admin Enable/Disable/Edit Features

## Overview
Enhanced admin management controls for instructors and students with Enable/Disable and Edit functionality.

## Features Implemented

### 1. Enable/Disable Instructors
- **UI**: Toggle button in Instructors table (Actions column)
- **Status Badge**: Shows "Enabled" (green) or "Disabled" (red)
- **Backend**: `PUT /api/admin/instructor/<id>/toggle`
- **Database**: Updates `enabled` field in `users` collection
- **Effect**: Disabled instructors cannot log in or access any routes

### 2. Enable/Disable Students
- **UI**: Toggle button in Students table (Actions column)
- **Status Badge**: Shows "Enabled" (green) or "Disabled" (red)
- **Backend**: `PUT /api/admin/student/<id>/toggle`
- **Database**: Updates `enabled` field in `users` collection
- **Effect**: Disabled students cannot log in or access any routes

### 3. Edit Instructors
- **UI**: Edit button opens modal with form
- **Fields**: Name, Email, Department
- **Backend**: `PUT /api/admin/instructor/<id>`
- **Database**: Updates instructor record in `users` collection

### 4. Edit Students
- **UI**: Edit button opens modal with form
- **Fields**: Name, Email, Department, Year, Section
- **Backend**: `PUT /api/admin/student/<id>`
- **Database**: Updates both `students` and `users` collections

## Backend Changes

### Files Modified

#### `backend/blueprints/admin.py`
- Added `toggle_instructor()` endpoint
- Added `toggle_student()` endpoint
- Added `update_instructor()` endpoint
- Added `update_student()` endpoint
- Updated `get_instructors()` to return `enabled` status
- Updated `get_students()` to return `enabled` status

#### `backend/blueprints/auth.py`
- Added check for `enabled` status during login
- Returns 403 error if account is disabled

#### `backend/utils/security.py`
- Added `enabled` check in `role_required()` decorator
- Prevents disabled users from accessing protected routes

## Frontend Changes

### Files Modified

#### `frontend/src/pages/AdminDashboard.tsx`
- Added Status column to both tables
- Added Enable/Disable buttons
- Added Edit buttons
- Added Edit modals for both instructors and students
- Implemented handlers:
  - `handleToggleInstructor()`
  - `handleToggleStudent()`
  - `handleUpdateInstructor()`
  - `handleUpdateStudent()`

#### `frontend/src/lib/api.ts`
- Added `toggleInstructor()` API method
- Added `toggleStudent()` API method
- Added `updateInstructor()` API method
- Added `updateStudent()` API method

## API Endpoints

### Toggle Instructor
```
PUT /api/admin/instructor/<instructor_id>/toggle
Authorization: Bearer <admin_token>

Response:
{
  "message": "Instructor enabled/disabled successfully",
  "enabled": true/false
}
```

### Toggle Student
```
PUT /api/admin/student/<student_id>/toggle
Authorization: Bearer <admin_token>

Response:
{
  "message": "Student enabled/disabled successfully",
  "enabled": true/false
}
```

### Update Instructor
```
PUT /api/admin/instructor/<instructor_id>
Authorization: Bearer <admin_token>
Content-Type: application/json

Body:
{
  "name": "Updated Name",
  "email": "updated@email.com",
  "department": "Updated Department"
}

Response:
{
  "message": "Instructor updated successfully"
}
```

### Update Student
```
PUT /api/admin/student/<student_id>
Authorization: Bearer <admin_token>
Content-Type: application/json

Body:
{
  "name": "Updated Name",
  "email": "updated@email.com",
  "department": "Updated Department",
  "year": "3",
  "section": "A"
}

Response:
{
  "message": "Student updated successfully"
}
```

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  password: String (hashed),
  email: String,
  name: String,
  role: String, // 'admin', 'instructor', 'student'
  enabled: Boolean, // NEW FIELD (default: true)
  department: String,
  created_at: DateTime
}
```

### Students Collection
```javascript
{
  _id: ObjectId,
  user_id: String, // Reference to users._id
  student_id: String,
  name: String,
  email: String,
  department: String,
  year: String,
  section: String,
  face_registered: Boolean,
  created_at: DateTime
}
```

## Security

### Login Protection
- Disabled users receive 403 error: "Account is disabled. Please contact administrator."
- Check happens after password verification

### Route Protection
- `role_required()` decorator checks `enabled` status
- Disabled users cannot access any protected routes
- Returns 403 error if account is disabled

## Testing

### Manual Testing Steps

1. **Start the system**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Login as Admin**:
   - Username: `admin`
   - Password: `admin123`

3. **Test Instructor Management**:
   - View instructors list
   - Click "Disable" on an instructor
   - Verify status changes to "Disabled" (red badge)
   - Try logging in as that instructor (should fail with 403)
   - Click "Enable" to re-enable
   - Click "Edit" to modify instructor details
   - Save changes and verify updates

4. **Test Student Management**:
   - View students list
   - Click "Disable" on a student
   - Verify status changes to "Disabled" (red badge)
   - Try logging in as that student (should fail with 403)
   - Click "Enable" to re-enable
   - Click "Edit" to modify student details
   - Save changes and verify updates

### Automated Testing
```bash
# Run test script
test_admin_features.bat
```

## UI/UX

### Table Layout
- **Instructors Table**: Name | Username | Email | Department | Status | Actions
- **Students Table**: Student ID | Name | Email | Department | Face Registered | Status | Actions

### Actions Column
- **Enable/Disable**: Orange/Green button (toggles based on current status)
- **Edit**: Blue button (opens modal)
- **Delete**: Red button (existing functionality)

### Edit Modals
- Modal overlay with form
- Pre-filled with current values
- Save/Cancel buttons
- Closes on successful save or cancel

### Status Badges
- **Enabled**: Green badge with "Enabled" text
- **Disabled**: Red badge with "Disabled" text

## Error Handling

### Backend
- Returns appropriate HTTP status codes
- Provides descriptive error messages
- Logs all operations for debugging

### Frontend
- Toast notifications for success/error
- Confirmation dialogs for destructive actions
- Form validation

## Notes

- All existing functionality (Add, Delete) remains unchanged
- No database migration required (enabled field defaults to true)
- Existing users without `enabled` field are treated as enabled
- Changes apply immediately to MongoDB
- No UI redesign - only added missing functionality

## Future Enhancements

Potential improvements:
- Bulk enable/disable operations
- Audit log for enable/disable actions
- Temporary disable with auto-enable date
- Reason field for disabling accounts
- Email notifications when account is disabled/enabled
