# Section Dropdown Debug Guide

## Issue
Section dropdown is not updating when course is selected in Download Reports page.

## What Was Changed

### Backend (`backend/blueprints/instructor.py`)
Added new endpoint: `/api/instructor/sections-by-course`
- Takes `course_name` as query parameter
- Returns sections that have had sessions for that course
- Filters by instructor's assigned sections

### Frontend API (`frontend/src/lib/api.ts`)
Added function: `getSectionsByCourse(courseName)`

### Frontend Reports Page (`frontend/src/pages/InstructorReports.tsx`)
- Updated `loadSectionsForCourse()` to call new API
- Added console.log for debugging
- useEffect triggers when `filters.course_name` changes

## How to Debug

### 1. Check Browser Console
Open browser DevTools (F12) and check Console tab when you:
1. Open Download Reports page
2. Select a course from dropdown

You should see:
```
Loading sections for course: CS101
Received sections: ["A", "B", "C"]
```

### 2. Check Network Tab
In DevTools Network tab, look for:
- Request to `/api/instructor/sections-by-course?course_name=CS101`
- Check if it returns 200 OK
- Check response body for sections array

### 3. Check Backend Logs
Look at the backend terminal for any errors when the API is called.

### 4. Test Backend Directly
Run: `python test_sections_endpoint.py`
(Note: Update credentials if needed)

## Expected Behavior

1. **Load page** → Instructor info loaded, courses populated
2. **Select course** → API call to get sections for that course
3. **Section dropdown updates** → Shows "Section A", "Section B", etc.
4. **Select section** → Can generate report

## Current Code

### Section Dropdown (InstructorReports.tsx line 313-318)
```tsx
{availableSections.map((section: string) => (
  <option key={section} value={section}>
    Section {section}
  </option>
))}
```

This displays: "Section A", "Section B", "Section C"

### useEffect (line 57-64)
```tsx
useEffect(() => {
  if (filters.course_name) {
    loadSectionsForCourse(filters.course_name);
  } else {
    setAvailableSections([]);
    setFilters(prev => ({ ...prev, section_id: '' }));
  }
}, [filters.course_name]);
```

Triggers when course changes.

## Troubleshooting

### If sections don't load:
1. **Hard refresh browser** (Ctrl + Shift + R)
2. **Check if frontend dev server is running**
3. **Check backend is running** on port 5000
4. **Check browser console** for errors
5. **Check network tab** for failed requests

### If dropdown shows nothing:
1. Check if `availableSections` array is populated (console.log)
2. Check if instructor has sections assigned
3. Check if there are sessions for the selected course

### If dropdown shows wrong format:
- Should show "Section A", not just "A"
- Check browser cache (hard refresh)

## Quick Test

1. Login as instructor
2. Go to Download Reports
3. Open browser console (F12)
4. Select a course
5. Watch console for logs
6. Check if section dropdown updates

## Files Modified

- `backend/blueprints/instructor.py` - Added `/sections-by-course` endpoint
- `frontend/src/lib/api.ts` - Added `getSectionsByCourse()` function  
- `frontend/src/pages/InstructorReports.tsx` - Updated section loading logic

## Backend Running
Backend should be running on http://localhost:5000
Check with: `curl http://localhost:5000/api/health` (if health endpoint exists)
