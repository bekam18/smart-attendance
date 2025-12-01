# Instructor Dashboard Upgrade Plan

## ✅ Already Working
- Login system
- Session creation and management
- Live webcam face recognition
- Real-time attendance list updates
- Duplicate prevention (already_marked status)
- Session end functionality

## 🔧 Features to Add

### 1. Attendance Records Page
**New Page:** `/instructor/records`
- View all past attendance across sessions
- Filter by date range, student, session
- Export to CSV/Excel
- Search functionality

### 2. Settings Page
**New Page:** `/instructor/settings`
- Change password
- Confidence threshold slider (0.50-0.95, default 0.60)
- Auto-capture interval (1-10 seconds, default 2)
- Save to user preferences in DB

### 3. Backend Endpoints to Add
- `GET /api/attendance/records` - Get all attendance with filters
- `GET /api/attendance/export` - Export attendance to CSV
- `GET /api/instructor/settings` - Get instructor settings
- `PUT /api/instructor/settings` - Update instructor settings
- `PUT /api/instructor/change-password` - Change password

### 4. Database Collections
- `user_settings` - Store instructor preferences
- `attendance` - Already exists, ensure proper indexing

## Implementation Order
1. Backend endpoints (attendance records, settings)
2. Frontend Records page
3. Frontend Settings page
4. Add navigation links to existing dashboard
5. Test end-to-end

## Files to Create/Modify
- `backend/blueprints/instructor.py` (new)
- `frontend/src/pages/AttendanceRecords.tsx` (new)
- `frontend/src/pages/InstructorSettings.tsx` (new)
- `frontend/src/lib/api.ts` (add new API calls)
- `frontend/src/App.tsx` (add new routes)
- `frontend/src/pages/InstructorDashboard.tsx` (add navigation buttons)
