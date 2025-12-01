# 🎯 Admin Dashboard Enhancements - Implementation Plan

## Overview
Comprehensive admin features without changing existing UI design.

---

## 1️⃣ View All Records Section

### Backend (admin.py)
- `GET /api/admin/attendance/all` - Get all attendance records
  - Filters: date, student, section, instructor
  - Returns: All students' attendance from all instructors
- `GET /api/admin/attendance/export/csv` - Export CSV
- `GET /api/admin/attendance/export/excel` - Export Excel

### Frontend
- New page: `AdminAllRecords.tsx`
- Filters: Date range, Student dropdown, Section dropdown, Instructor dropdown
- Export buttons: CSV, Excel
- Table: Date, Time, Student, Section, Instructor, Confidence

---

## 2️⃣ Admin Settings Section

### Backend (admin.py)
- `GET /api/admin/settings` - Get admin settings
- `PUT /api/admin/settings` - Update settings
  - face_recognition_threshold
  - session_timeout_minutes
- `GET /api/admin/active-sessions` - Get currently running sessions

### Frontend
- New page: `AdminSettings.tsx`
- Face recognition threshold slider (50%-95%)
- Session timeout input (minutes/hours)
- Active sessions display
- Save button

### Database
- New collection: `admin_settings`
```javascript
{
  face_recognition_threshold: 0.60,
  session_timeout_minutes: 120,
  updated_at: DateTime
}
```

---

## 3️⃣ Daily Dashboard Display Logic

### Backend
- Modify `GET /api/admin/stats` to accept date parameter
- Default: Today's last 12 hours
- Optional: Previous dates

### Frontend (AdminDashboard.tsx)
- Add date picker for viewing previous days
- Default: Show today's attendance (last 12 hours)
- Stats update based on selected date
- All data still saved permanently in DB

---

## 4️⃣ Enable/Disable & Edit Users

### Backend (admin.py)
- `PUT /api/admin/instructor/:id/toggle` - Enable/Disable instructor
- `PUT /api/admin/student/:id/toggle` - Enable/Disable student
- `PUT /api/admin/instructor/:id` - Edit instructor
- `PUT /api/admin/student/:id` - Edit student

### Database Schema Update
Add `enabled` field to users:
```javascript
{
  _id: ObjectId,
  username: "instructor",
  enabled: true,  // NEW FIELD
  ...
}
```

### Frontend (AdminDashboard.tsx)
- Add "Enable/Disable" toggle button
- Add "Edit" button (opens modal)
- Keep existing "Delete" button
- Status badge (Active/Disabled)

---

## Implementation Order

1. ✅ Backend: Admin attendance endpoints
2. ✅ Backend: Admin settings endpoints
3. ✅ Backend: Enable/Disable endpoints
4. ✅ Backend: Edit endpoints
5. ✅ Frontend: AdminAllRecords page
6. ✅ Frontend: AdminSettings page
7. ✅ Frontend: Update AdminDashboard with new features
8. ✅ Frontend: Add routes to App.tsx
9. ✅ Frontend: Update API functions
10. ✅ Testing & Documentation

---

## Files to Create/Modify

### Backend
- `backend/blueprints/admin.py` - Add new endpoints
- `backend/db/mongo.py` - No changes needed

### Frontend
- `frontend/src/pages/AdminAllRecords.tsx` - NEW
- `frontend/src/pages/AdminSettings.tsx` - NEW
- `frontend/src/pages/AdminDashboard.tsx` - MODIFY (add buttons)
- `frontend/src/App.tsx` - ADD ROUTES
- `frontend/src/lib/api.ts` - ADD API FUNCTIONS

---

## Key Requirements

✅ No UI redesign - keep existing design  
✅ Add functionality only  
✅ All data to MongoDB  
✅ CSV/Excel exports working  
✅ Daily dashboard with date picker  
✅ Enable/Disable for users  
✅ Edit functionality  
✅ Keep existing Delete working  

---

**Ready to implement!** 🚀
