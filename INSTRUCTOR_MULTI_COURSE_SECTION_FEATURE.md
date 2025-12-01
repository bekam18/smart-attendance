# Instructor Multi-Course & Multi-Section Feature

## Overview
Allow instructors to be assigned to multiple courses and multiple sections.

## Current State
- Instructors have single `course_name` field
- Instructors have single `class_year` field
- No section assignment

## Required Changes

### 1. Database Schema Update

**Instructor Model Changes:**
```javascript
{
  username: String,
  email: String,
  name: String,
  department: String,
  courses: [String],  // NEW: Array of course names
  sections: [String], // NEW: Array of sections (A, B, C, D)
  lab_session: Boolean,
  theory_session: Boolean
}
```

### 2. Backend Changes

**File: `backend/blueprints/admin.py`**

Update `add_instructor` endpoint:
```python
@admin_bp.route('/instructors', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_instructor():
    data = request.json
    
    # Validate courses (array)
    courses = data.get('courses', [])
    if not courses or len(courses) == 0:
        return jsonify({'error': 'At least one course required'}), 400
    
    # Validate sections (array)
    sections = data.get('sections', [])
    if not sections or len(sections) == 0:
        return jsonify({'error': 'At least one section required'}), 400
    
    # Create instructor with arrays
    instructor_data = {
        'username': data['username'],
        'email': data['email'],
        'name': data['name'],
        'department': data.get('department', ''),
        'courses': courses,  # Array
        'sections': sections,  # Array
        'lab_session': data.get('lab_session', False),
        'theory_session': data.get('theory_session', False)
    }
    
    # ... rest of logic
```

### 3. Frontend Changes

**File: `frontend/src/pages/AdminDashboard.tsx`**

#### A. Update State
```typescript
const [instructorFormData, setInstructorFormData] = useState({
  username: '',
  password: '',
  email: '',
  name: '',
  department: '',
  courses: [] as string[],      // NEW: Array
  sections: [] as string[],     // NEW: Array
  lab_session: false,
  theory_session: false
});
```

#### B. Add Multi-Select Components

Replace single course input with multi-select:
```tsx
{/* Multiple Course Selection */}
<div className="col-span-2 border rounded-lg p-4 bg-gray-50">
  <label className="block text-sm font-medium text-gray-700 mb-3">
    Courses <span className="text-red-500">*</span>
  </label>
  <div className="grid grid-cols-2 gap-3">
    {['Data Structures', 'Algorithms', 'Database Systems', 'Web Development', 
      'Machine Learning', 'Computer Networks'].map((course) => (
      <label key={course} className="flex items-center space-x-2 cursor-pointer">
        <input
          type="checkbox"
          checked={instructorFormData.courses.includes(course)}
          onChange={(e) => {
            if (e.target.checked) {
              setInstructorFormData({
                ...instructorFormData,
                courses: [...instructorFormData.courses, course]
              });
            } else {
              setInstructorFormData({
                ...instructorFormData,
                courses: instructorFormData.courses.filter(c => c !== course)
              });
            }
          }}
          className="w-4 h-4 text-blue-600 rounded"
        />
        <span className="text-sm text-gray-700">{course}</span>
      </label>
    ))}
  </div>
  <p className="text-xs text-gray-500 mt-2">
    Selected: {instructorFormData.courses.length} course(s)
  </p>
</div>

{/* Multiple Section Selection */}
<div className="col-span-2 border rounded-lg p-4 bg-gray-50">
  <label className="block text-sm font-medium text-gray-700 mb-3">
    Sections <span className="text-red-500">*</span>
  </label>
  <div className="flex space-x-6">
    {['A', 'B', 'C', 'D'].map((section) => (
      <label key={section} className="flex items-center space-x-2 cursor-pointer">
        <input
          type="checkbox"
          checked={instructorFormData.sections.includes(section)}
          onChange={(e) => {
            if (e.target.checked) {
              setInstructorFormData({
                ...instructorFormData,
                sections: [...instructorFormData.sections, section]
              });
            } else {
              setInstructorFormData({
                ...instructorFormData,
                sections: instructorFormData.sections.filter(s => s !== section)
              });
            }
          }}
          className="w-4 h-4 text-blue-600 rounded"
        />
        <span className="text-gray-700 font-medium">Section {section}</span>
      </label>
    ))}
  </div>
  <p className="text-xs text-gray-500 mt-2">
    Selected: {instructorFormData.sections.length} section(s)
  </p>
</div>
```

#### C. Update Instructor Table Display

Add Sections column to instructor table:
```tsx
<thead className="bg-gray-50">
  <tr>
    <th>Name</th>
    <th>Email</th>
    <th>Department</th>
    <th>Courses</th>
    <th>Sections</th>  {/* NEW */}
    <th>Session Types</th>
    <th>Status</th>
    <th>Actions</th>
  </tr>
</thead>
<tbody>
  {instructors.map((instructor) => (
    <tr key={instructor.id}>
      <td>{instructor.name}</td>
      <td>{instructor.email}</td>
      <td>{instructor.department}</td>
      <td>
        <div className="flex flex-wrap gap-1">
          {(instructor.courses || [instructor.course_name]).map((course, idx) => (
            <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
              {course}
            </span>
          ))}
        </div>
      </td>
      <td>
        <div className="flex flex-wrap gap-1">
          {(instructor.sections || []).map((section, idx) => (
            <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
              {section}
            </span>
          ))}
        </div>
      </td>
      {/* ... rest of columns */}
    </tr>
  ))}
</tbody>
```

#### D. Update Form Validation

```typescript
const handleAddInstructor = async (e: React.FormEvent) => {
  e.preventDefault();
  
  // Validate courses
  if (instructorFormData.courses.length === 0) {
    toast.error('Please select at least one course');
    return;
  }
  
  // Validate sections
  if (instructorFormData.sections.length === 0) {
    toast.error('Please select at least one section');
    return;
  }
  
  // Validate session types
  if (!instructorFormData.lab_session && !instructorFormData.theory_session) {
    toast.error('Please select at least one session type');
    return;
  }
  
  try {
    await adminAPI.addInstructor(instructorFormData);
    toast.success('Instructor added successfully');
    // Reset form
    setInstructorFormData({
      username: '',
      password: '',
      email: '',
      name: '',
      department: '',
      courses: [],
      sections: [],
      lab_session: false,
      theory_session: false
    });
    loadData();
  } catch (error: any) {
    toast.error(error.response?.data?.error || 'Failed to add instructor');
  }
};
```

### 4. Migration Script

Create `backend/migrate_instructor_courses_sections.py`:
```python
"""
Migrate existing instructors to new multi-course/section format
"""
from db.mongo import init_db

db = init_db()

# Update all instructors
result = db.users.update_many(
    {'role': 'instructor'},
    [{
        '$set': {
            'courses': {
                '$cond': {
                    'if': {'$ifNull': ['$course_name', False]},
                    'then': ['$course_name'],
                    'else': []
                }
            },
            'sections': []  # Default empty, admin will update
        }
    }]
)

print(f"Updated {result.modified_count} instructors")
```

### 5. Implementation Steps

1. **Backend First:**
   - Update admin.py endpoints
   - Test with Postman/curl

2. **Database Migration:**
   - Run migration script
   - Verify data

3. **Frontend:**
   - Update form state
   - Add multi-select UI
   - Update table display
   - Test form submission

4. **Testing:**
   - Add instructor with multiple courses
   - Add instructor with multiple sections
   - Verify display in table
   - Test edit functionality

### 6. Benefits

- ✅ Instructors can teach multiple courses
- ✅ Instructors can handle multiple sections
- ✅ Better flexibility for scheduling
- ✅ Accurate representation of teaching assignments

### 7. Example Data

```json
{
  "name": "Dr. Smith",
  "email": "smith@university.edu",
  "courses": ["Data Structures", "Algorithms", "Web Development"],
  "sections": ["A", "B"],
  "lab_session": true,
  "theory_session": true
}
```

This instructor teaches 3 courses across 2 sections with both lab and theory sessions.

---

**Status**: Ready for implementation
**Priority**: Medium
**Estimated Time**: 2-3 hours
