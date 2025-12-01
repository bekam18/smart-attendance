# Admin Features Quick Start

## What's New?

Admin can now:
1. ✅ **Enable/Disable** instructors and students
2. ✅ **Edit** instructor and student details
3. ✅ **Delete** instructors and students (existing)
4. ✅ **Add** new instructors and students (existing)

## Quick Access

### Login as Admin
- URL: `http://localhost:5173/login`
- Username: `admin`
- Password: `admin123`

### Admin Dashboard
- URL: `http://localhost:5173/admin`
- View all instructors and students
- Manage user accounts

## Features

### 1. Enable/Disable Users

**Instructors:**
- Click "Disable" button to prevent login
- Click "Enable" button to restore access
- Status badge shows current state

**Students:**
- Click "Disable" button to prevent login
- Click "Enable" button to restore access
- Status badge shows current state

**Effect:**
- Disabled users cannot log in
- Disabled users cannot access any routes
- Error message: "Account is disabled. Please contact administrator."

### 2. Edit User Details

**Instructors:**
- Click "Edit" button
- Update: Name, Email, Department
- Click "Save" to apply changes

**Students:**
- Click "Edit" button
- Update: Name, Email, Department, Year, Section
- Click "Save" to apply changes

### 3. Delete Users

**Instructors:**
- Click "Delete" button
- Confirm deletion
- Instructor removed from system

**Students:**
- Click "Delete" button
- Confirm deletion
- Student and attendance records removed

## Table Columns

### Instructors Table
| Column | Description |
|--------|-------------|
| Name | Full name |
| Username | Login username |
| Email | Email address |
| Department | Department name |
| Status | Enabled/Disabled badge |
| Actions | Enable/Disable, Edit, Delete buttons |

### Students Table
| Column | Description |
|--------|-------------|
| Student ID | Unique student identifier |
| Name | Full name |
| Email | Email address |
| Department | Department name |
| Face Registered | Yes/No badge |
| Status | Enabled/Disabled badge |
| Actions | Enable/Disable, Edit, Delete buttons |

## Testing

### Test Enable/Disable
1. Login as admin
2. Disable an instructor/student
3. Logout
4. Try logging in as that user
5. Should see: "Account is disabled. Please contact administrator."
6. Login as admin again
7. Enable the user
8. User can now login successfully

### Test Edit
1. Login as admin
2. Click "Edit" on any user
3. Modify details in the modal
4. Click "Save"
5. Verify changes appear in the table
6. Verify changes in database

## API Endpoints

All endpoints require admin authentication:

```
PUT /api/admin/instructor/<id>/toggle    # Enable/Disable instructor
PUT /api/admin/student/<id>/toggle       # Enable/Disable student
PUT /api/admin/instructor/<id>           # Update instructor
PUT /api/admin/student/<id>              # Update student
DELETE /api/admin/instructor/<id>        # Delete instructor
DELETE /api/admin/student/<id>           # Delete student
```

## Troubleshooting

### User can still login after disabling
- Check if backend is running
- Verify MongoDB connection
- Check browser console for errors
- Clear browser cache and cookies

### Edit modal not showing
- Check browser console for errors
- Verify frontend is running
- Refresh the page

### Changes not saving
- Check backend logs
- Verify MongoDB is running
- Check network tab in browser dev tools

## Database

### Check User Status
```javascript
// In MongoDB shell or Compass
db.users.find({ enabled: false })  // Find disabled users
db.users.find({ enabled: true })   // Find enabled users
```

### Manually Enable/Disable
```javascript
// Enable user
db.users.updateOne(
  { username: "instructor1" },
  { $set: { enabled: true } }
)

// Disable user
db.users.updateOne(
  { username: "instructor1" },
  { $set: { enabled: false } }
)
```

## Notes

- Default value for `enabled` is `true`
- Existing users without `enabled` field are treated as enabled
- Admin accounts cannot be disabled through the UI
- Changes apply immediately
- No system restart required
