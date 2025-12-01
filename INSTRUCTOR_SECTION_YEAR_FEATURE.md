# Instructor Section & Year Selection Feature

## Overview
Instructors can now select **Section** (A, B, C, D) and **Year** (1st-4th) from dropdowns when creating attendance sessions. This allows them to take attendance for specific sections and see only students registered to those sections.

## Changes Made

### 1. Admin Dashboard - Instructor Form

**File**: `frontend/src/pages/AdminDashboard.tsx`

#### Updated Form Fields:
- **Removed**: Multiple courses input field
- **Added**: Year dropdown (1st Year, 2nd Year, 3rd Year, 4th Year)
- **Added**: Sections checkboxes (A, B, C, D)

#### Form State:
```typescript
const [instructorFormData, setInstructorFormData] = useState({
  username: '',
  password: '',
  email: '',
  name: '',
  department: '',
  sections: [] as string[],  // NEW: Array of sections
  year: '',                   // NEW: Year level
  lab_session: false,
  theory_session: false
});
```

#### Validation:
- At least one section must be selected
- Year level is required
- At least one session type (Lab/Theory) required

### 2. Instructor Dashboard - Session Creation

**File**: `frontend/src/pages/InstructorDashboard.tsx`

#### Updated Session Form:
- **Changed**: Section from text input to dropdown
- **Changed**: Year from text input to dropdown
- **Made**: Course field optional

#### Section Dropdown:
```tsx
<select value={section} onChange={(e) => setSection(e.target.value)} required>
  <option value="">Select Section...</option>
  <option value="A">Section A</option>
  <option value="B">Section B</option>
  <option value="C">Section C</option>
  <option value="D">Section D</option>
</select>
```

#### Year Dropdown:
```tsx
<select value={year} onChange={(e) => setYear(e.target.value)} required>
  <option value="">Select Year...</option>
  <option value="1st Year">1st Year</option>
  <option value="2nd Year">2nd Year</option>
  <option value="3rd Year">3rd Year</option>
  <option value="4th Year">4th Year</option>
</select>
```

## How It Works

### Admin Workflow

1. **Add Instructor**:
   - Fill in basic info (username, email, name, department)
   - Select **Year Level** from dropdown
   - Select **Sections** (can select multiple: A, B, C, D)
   - Select **Session Types** (Lab/Theory)
   - Submit

2. **Instructor Data Stored**:
```json
{
  "name": "Dr. Smith",
  "year": "3rd Year",
  "sections": ["A", "B"],
  "session_types": ["lab", "theory"]
}
```

### Instructor Workflow

1. **Create Session**:
   - Select **Session Type** (Lab/Theory)
   - Select **Time Block** (Morning/Afternoon)
   - Enter **Session Name**
   - Select **Section** from dropdown (A, B, C, or D)
   - Select **Year** from dropdown (1st-4th Year)
   - Optionally enter **Course Name**
   - Click "Create & Start"

2. **Session Data**:
```json
{
  "name": "Data Structures Lab",
  "session_type": "lab",
  "time_block": "morning",
  "section_id": "A",
  "year": "3rd Year",
  "course": "Computer Science"
}
```

3. **Take Attendance**:
   - Students from selected section and year are shown
   - Face recognition records attendance
   - Only students matching section/year criteria are recognized

## Backend Integration

### Instructor Model
```python
{
  'username': 'dr.smith',
  'name': 'Dr. John Smith',
  'year': '3rd Year',
  'sections': ['A', 'B'],  # Array of sections
  'session_types': ['lab', 'theory']
}
```

### Session Model
```python
{
  'name': 'Data Structures Lab',
  'instructor_id': '...',
  'section_id': 'A',
  'year': '3rd Year',
  'session_type': 'lab',
  'time_block': 'morning',
  'course_name': 'Computer Science'  # Optional
}
```

### Student Filtering
When taking attendance, the system filters students by:
- `section` = selected section (A, B, C, or D)
- `year` = selected year (1st-4th Year)

## Benefits

✅ **Clear Section Management**: Instructors know exactly which section they're teaching
✅ **Year-Based Organization**: Easy to organize by academic year
✅ **Accurate Attendance**: Only students from selected section/year are shown
✅ **Flexible Assignment**: Instructors can teach multiple sections
✅ **Optional Course**: Course name is optional, focusing on section/year
✅ **User-Friendly**: Dropdowns prevent typos and ensure consistency

## UI Examples

### Admin - Add Instructor Form

```
┌─────────────────────────────────────────┐
│ Add New Instructor                      │
├─────────────────────────────────────────┤
│ Username: [dr.smith              ]      │
│ Password: [••••••••              ]      │
│ Email:    [smith@university.edu  ]      │
│ Name:     [Dr. John Smith        ]      │
│ Dept:     [Computer Science      ]      │
│                                         │
│ Year Level: [3rd Year ▼]               │
│                                         │
│ Sections:                               │
│ ☑ Section A  ☑ Section B               │
│ ☐ Section C  ☐ Section D               │
│ Selected: 2 section(s)                  │
│                                         │
│ Session Types:                          │
│ ☑ Lab Session  ☑ Theory Session        │
│                                         │
│ [Add Instructor] [Cancel]               │
└─────────────────────────────────────────┘
```

### Instructor - Create Session Form

```
┌─────────────────────────────────────────┐
│ Create New Session                      │
├─────────────────────────────────────────┤
│ Session Type: [Lab ▼]                   │
│                                         │
│ Time Block:                             │
│ [🌅 Morning ✓]  [🌆 Afternoon]         │
│                                         │
│ Session Name: [Data Structures Lab]     │
│                                         │
│ Section: [Section A ▼]                  │
│ Year:    [3rd Year ▼]                   │
│                                         │
│ Course: [Computer Science] (Optional)   │
│                                         │
│ [Create & Start] [Cancel]               │
└─────────────────────────────────────────┘
```

### Instructor - Active Session

```
┌─────────────────────────────────────────┐
│ Data Structures Lab                     │
│ [Lab] [🌅 Morning]                      │
│ Section A • 3rd Year                    │
├─────────────────────────────────────────┤
│ Students Present: 15/30                 │
│                                         │
│ [Camera View]                           │
│                                         │
│ Recent Attendance:                      │
│ ✓ John Doe - 09:15 AM                   │
│ ✓ Jane Smith - 09:16 AM                 │
│ ✓ Bob Johnson - 09:17 AM                │
└─────────────────────────────────────────┘
```

## Validation Rules

### Admin - Add Instructor
1. ✅ At least one section must be selected
2. ✅ Year level is required
3. ✅ At least one session type required
4. ✅ All basic fields (username, email, name) required

### Instructor - Create Session
1. ✅ Session type required
2. ✅ Time block required
3. ✅ Section required (dropdown)
4. ✅ Year required (dropdown)
5. ✅ Session name required
6. ⚪ Course is optional

## Database Queries

### Get Students for Session
```python
# Filter students by section and year
students = db.students.find({
    'section': 'A',
    'year': '3rd Year',
    'enabled': True
})
```

### Get Attendance Records
```python
# Filter attendance by section and year
attendance = db.attendance.find({
    'section_id': 'A',
    'year': '3rd Year',
    'instructor_id': instructor_id
})
```

## Migration Notes

### Existing Instructors
- Old instructors with `course_name` field still work
- Can be updated to use new `sections` and `year` fields
- Backward compatible

### Existing Sessions
- Old sessions without section/year still accessible
- New sessions will have section/year data
- No data loss

## Testing Checklist

### Admin Dashboard
- [ ] Add instructor with year and sections
- [ ] Validation: Try submitting without year
- [ ] Validation: Try submitting without sections
- [ ] Verify instructor appears in table
- [ ] Edit instructor details

### Instructor Dashboard
- [ ] Create session with section dropdown
- [ ] Create session with year dropdown
- [ ] Validation: Try submitting without section
- [ ] Validation: Try submitting without year
- [ ] Verify session shows section and year
- [ ] Take attendance for specific section

### Attendance
- [ ] Verify only students from selected section appear
- [ ] Verify only students from selected year appear
- [ ] Record attendance successfully
- [ ] View attendance records filtered by section/year

## Files Modified

### Frontend
- ✅ `frontend/src/pages/AdminDashboard.tsx`
  - Updated instructor form state
  - Added year dropdown
  - Added sections checkboxes
  - Updated validation

- ✅ `frontend/src/pages/InstructorDashboard.tsx`
  - Changed section to dropdown
  - Changed year to dropdown
  - Made course optional

### Backend
- ⚪ `backend/blueprints/admin.py` (may need updates)
  - Accept `sections` array
  - Accept `year` field
  - Store in database

- ⚪ `backend/blueprints/instructor.py` (may need updates)
  - Filter students by section/year
  - Return section-specific data

## Next Steps

1. **Test the changes**:
   ```bash
   # Start backend
   cd backend && python app.py
   
   # Start frontend
   cd frontend && npm run dev
   ```

2. **Add instructor** with sections and year

3. **Create session** with section/year dropdowns

4. **Take attendance** and verify filtering works

## Status

✅ **Frontend**: Complete
⚪ **Backend**: May need updates for section/year filtering
⚪ **Testing**: Pending
⚪ **Documentation**: Complete

---

**Date**: December 1, 2025
**Feature**: Section & Year Selection for Instructors
**Status**: Frontend Complete, Backend Review Needed
