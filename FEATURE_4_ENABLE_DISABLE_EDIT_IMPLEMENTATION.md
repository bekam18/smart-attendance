# 🎯 Feature 4: Enable/Disable & Edit Users - Implementation Guide

## ✅ Backend Complete

All backend endpoints have been added to `backend/blueprints/admin.py`:

### New Endpoints

1. **PUT `/api/admin/instructor/<id>/toggle`** - Enable/Disable instructor
2. **PUT `/api/admin/student/<id>/toggle`** - Enable/Disable student  
3. **PUT `/api/admin/instructor/<id>`** - Edit instructor details
4. **PUT `/api/admin/student/<id>`** - Edit student details

### Database Schema Update

Add `enabled` field to users:
```javascript
{
  _id: ObjectId,
  username: "instructor",
  enabled: true,  // NEW FIELD (default: true)
  ...
}
```

---

## 🔧 Frontend Implementation Needed

### Step 1: Add API Functions to `frontend/src/lib/api.ts`

```typescript
// Add to adminAPI object:

toggleInstructor: (instructorId: string) =>
  api.put(`/api/admin/instructor/${instructorId}/toggle`),

toggleStudent: (studentId: string) =>
  api.put(`/api/admin/student/${studentId}/toggle`),

updateInstructor: (instructorId: string, data: any) =>
  api.put(`/api/admin/instructor/${instructorId}`, data),

updateStudent: (studentId: string, data: any) =>
  api.put(`/api/admin/student/${studentId}`, data),
```

### Step 2: Update `frontend/src/pages/AdminDashboard.tsx`

#### Add State for Edit Modals

```typescript
const [editingInstructor, setEditingInstructor] = useState<any>(null);
const [editingStudent, setEditingStudent] = useState<any>(null);
```

#### Add Handler Functions

```typescript
const handleToggleInstructor = async (instructorId: string) => {
  try {
    await adminAPI.toggleInstructor(instructorId);
    toast.success('Instructor status updated');
    loadData(selectedDate || undefined);
  } catch (error: any) {
    toast.error('Failed to update instructor');
  }
};

const handleToggleStudent = async (studentId: string) => {
  try {
    await adminAPI.toggleStudent(studentId);
    toast.success('Student status updated');
    loadData(selectedDate || undefined);
  } catch (error: any) {
    toast.error('Failed to update student');
  }
};

const handleUpdateInstructor = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    await adminAPI.updateInstructor(editingInstructor.id, {
      name: editingInstructor.name,
      email: editingInstructor.email,
      department: editingInstructor.department
    });
    toast.success('Instructor updated successfully');
    setEditingInstructor(null);
    loadData(selectedDate || undefined);
  } catch (error: any) {
    toast.error('Failed to update instructor');
  }
};

const handleUpdateStudent = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    await adminAPI.updateStudent(editingStudent.id, {
      name: editingStudent.name,
      email: editingStudent.email,
      department: editingStudent.department,
      year: editingStudent.year,
      section: editingStudent.section
    });
    toast.success('Student updated successfully');
    setEditingStudent(null);
    loadData(selectedDate || undefined);
  } catch (error: any) {
    toast.error('Failed to update student');
  }
};
```

#### Update Instructors Table - Add Status Badge and Buttons

Replace the Actions column in instructors table:

```typescript
<td className="px-6 py-4 whitespace-nowrap">
  <div className="flex items-center space-x-2">
    {/* Status Badge */}
    <span className={`px-2 py-1 rounded-full text-xs ${
      instructor.enabled !== false 
        ? 'bg-green-100 text-green-800' 
        : 'bg-red-100 text-red-800'
    }`}>
      {instructor.enabled !== false ? 'Active' : 'Disabled'}
    </span>
    
    {/* Toggle Button */}
    <button
      onClick={() => handleToggleInstructor(instructor.id)}
      className={`px-3 py-1 rounded text-xs ${
        instructor.enabled !== false
          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
          : 'bg-green-100 text-green-800 hover:bg-green-200'
      }`}
    >
      {instructor.enabled !== false ? 'Disable' : 'Enable'}
    </button>
    
    {/* Edit Button */}
    <button
      onClick={() => setEditingInstructor(instructor)}
      className="text-blue-600 hover:text-blue-800"
    >
      Edit
    </button>
    
    {/* Delete Button (existing) */}
    <button
      onClick={() => handleDeleteInstructor(instructor.id)}
      className="text-red-600 hover:text-red-800"
    >
      Delete
    </button>
  </div>
</td>
```

#### Update Students Table - Add Status Badge and Buttons

Replace the Actions column in students table:

```typescript
<td className="px-6 py-4 whitespace-nowrap">
  <div className="flex items-center space-x-2">
    {/* Status Badge */}
    <span className={`px-2 py-1 rounded-full text-xs ${
      student.enabled !== false 
        ? 'bg-green-100 text-green-800' 
        : 'bg-red-100 text-red-800'
    }`}>
      {student.enabled !== false ? 'Active' : 'Disabled'}
    </span>
    
    {/* Toggle Button */}
    <button
      onClick={() => handleToggleStudent(student.id)}
      className={`px-3 py-1 rounded text-xs ${
        student.enabled !== false
          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
          : 'bg-green-100 text-green-800 hover:bg-green-200'
      }`}
    >
      {student.enabled !== false ? 'Disable' : 'Enable'}
    </button>
    
    {/* Edit Button */}
    <button
      onClick={() => setEditingStudent(student)}
      className="text-blue-600 hover:text-blue-800"
    >
      Edit
    </button>
    
    {/* Delete Button (existing) */}
    <button
      onClick={() => handleDeleteStudent(student.id)}
      className="text-red-600 hover:text-red-800"
    >
      Delete
    </button>
  </div>
</td>
```

#### Add Edit Modal for Instructor

Add before the closing `</Layout>` tag:

```typescript
{/* Edit Instructor Modal */}
{editingInstructor && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
      <h3 className="text-lg font-semibold mb-4">Edit Instructor</h3>
      <form onSubmit={handleUpdateInstructor} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Name</label>
          <input
            type="text"
            value={editingInstructor.name}
            onChange={(e) => setEditingInstructor({...editingInstructor, name: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={editingInstructor.email}
            onChange={(e) => setEditingInstructor({...editingInstructor, email: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Department</label>
          <input
            type="text"
            value={editingInstructor.department}
            onChange={(e) => setEditingInstructor({...editingInstructor, department: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
        <div className="flex space-x-2">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Save Changes
          </button>
          <button
            type="button"
            onClick={() => setEditingInstructor(null)}
            className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
)}
```

#### Add Edit Modal for Student

```typescript
{/* Edit Student Modal */}
{editingStudent && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
      <h3 className="text-lg font-semibold mb-4">Edit Student</h3>
      <form onSubmit={handleUpdateStudent} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Name</label>
          <input
            type="text"
            value={editingStudent.name}
            onChange={(e) => setEditingStudent({...editingStudent, name: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={editingStudent.email}
            onChange={(e) => setEditingStudent({...editingStudent, email: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Section</label>
          <select
            value={editingStudent.section}
            onChange={(e) => setEditingStudent({...editingStudent, section: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
          >
            <option value="A">Section A</option>
            <option value="B">Section B</option>
            <option value="C">Section C</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Department</label>
          <input
            type="text"
            value={editingStudent.department}
            onChange={(e) => setEditingStudent({...editingStudent, department: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Year</label>
          <input
            type="text"
            value={editingStudent.year}
            onChange={(e) => setEditingStudent({...editingStudent, year: e.target.value})}
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
        <div className="flex space-x-2">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Save Changes
          </button>
          <button
            type="button"
            onClick={() => setEditingStudent(null)}
            className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
)}
```

---

## 🎨 UI Preview

### Instructors Table
```
┌────────────────────────────────────────────────────────────┐
│ Name     │ Username │ Email    │ Dept    │ Actions         │
├────────────────────────────────────────────────────────────┤
│ Dr.Smith │ inst1    │ dr@...   │ CS      │ [Active]        │
│          │          │          │         │ [Disable] [Edit] [Delete] │
├────────────────────────────────────────────────────────────┤
│ Prof.Doe │ inst2    │ prof@... │ Math    │ [Disabled]      │
│          │          │          │         │ [Enable] [Edit] [Delete]  │
└────────────────────────────────────────────────────────────┘
```

### Students Table
```
┌────────────────────────────────────────────────────────────┐
│ ID    │ Name   │ Email  │ Dept │ Section │ Actions        │
├────────────────────────────────────────────────────────────┤
│ STU001│ Nabila │ nab@...│ CS   │ A       │ [Active]       │
│       │        │        │      │         │ [Disable] [Edit] [Delete] │
└────────────────────────────────────────────────────────────┘
```

---

## ✅ Features Summary

### Enable/Disable
- Toggle button changes color based on status
- Active users: Yellow "Disable" button
- Disabled users: Green "Enable" button
- Status badge shows current state

### Edit
- Click "Edit" opens modal
- Pre-filled with current data
- Save updates database
- Cancel closes modal

### Delete
- Existing functionality preserved
- Still shows confirmation dialog
- Permanently removes user

---

## 🧪 Testing

1. **Toggle Instructor**
   - Click "Disable" on active instructor
   - Status should change to "Disabled"
   - Button should change to "Enable"

2. **Edit Instructor**
   - Click "Edit"
   - Change name/email/department
   - Click "Save Changes"
   - Table should update

3. **Toggle Student**
   - Click "Disable" on active student
   - Status should change
   - Button should change

4. **Edit Student**
   - Click "Edit"
   - Change details including section
   - Save and verify update

---

**Implementation is ready! Follow the steps above to complete Feature 4.** 🚀
