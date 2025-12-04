import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { Users, UserPlus, BarChart3, Download, FileText, Settings } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [instructors, setInstructors] = useState<any[]>([]);
  const [showAddInstructor, setShowAddInstructor] = useState(false);
  const [showAddStudent, setShowAddStudent] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>(''); // Empty = today
  const [editingInstructor, setEditingInstructor] = useState<any>(null);
  const [editingStudent, setEditingStudent] = useState<any>(null);
  const [instructorFormData, setInstructorFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: '',
    department: '',
    course_name: '',  // Keep for backward compatibility
    courses: [] as string[],  // New multi-course field
    class_year: '',
    lab_session: false,
    theory_session: false
  });
  const [newCourse, setNewCourse] = useState('');
  const [studentFormData, setStudentFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: '',
    student_id: '',
    department: '',
    year: '',
    section: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (date?: string) => {
    try {
      const [statsRes, studentsRes, instructorsRes] = await Promise.all([
        adminAPI.getStats(date),
        adminAPI.getStudents(),
        adminAPI.getInstructors()
      ]);
      
      setStats(statsRes.data);
      setStudents(studentsRes.data);
      setInstructors(instructorsRes.data);
    } catch (error: any) {
      toast.error('Failed to load data');
    }
  };

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    loadData(date || undefined);
  };

  const handleAddInstructor = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate at least one course
    if (instructorFormData.courses.length === 0) {
      toast.error('Please add at least one course');
      return;
    }
    
    // Validate at least one session type is selected
    if (!instructorFormData.lab_session && !instructorFormData.theory_session) {
      toast.error('Please select at least one session type (Lab or Theory)');
      return;
    }
    
    try {
      await adminAPI.addInstructor(instructorFormData);
      toast.success('Instructor added successfully');
      setShowAddInstructor(false);
      setInstructorFormData({ 
        username: '', 
        password: '', 
        email: '', 
        name: '', 
        department: '',
        course_name: '',
        courses: [],
        class_year: '',
        lab_session: false,
        theory_session: false
      });
      setNewCourse('');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to add instructor');
    }
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await adminAPI.addStudent(studentFormData);
      toast.success('Student added successfully');
      setShowAddStudent(false);
      setStudentFormData({ username: '', password: '', email: '', name: '', student_id: '', department: '', year: '', section: '' });
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to add student');
    }
  };

  const handleDeleteInstructor = async (instructorId: string) => {
    if (!confirm('Are you sure you want to delete this instructor?')) return;
    
    try {
      await adminAPI.deleteInstructor(instructorId);
      toast.success('Instructor deleted successfully');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to delete instructor');
    }
  };

  const handleDeleteStudent = async (studentId: string) => {
    if (!confirm('Are you sure you want to delete this student?')) return;
    
    try {
      await adminAPI.deleteStudent(studentId);
      toast.success('Student deleted successfully');
      loadData(selectedDate || undefined);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to delete student');
    }
  };

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

  return (
    <Layout title="Admin Dashboard">
      <div className="space-y-6">
        {/* Date Selector and Quick Actions */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                View Date
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {selectedDate && (
              <button
                onClick={() => handleDateChange('')}
                className="mt-6 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Today
              </button>
            )}
            {!selectedDate && (
              <div className="mt-6 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm">
                Showing today's last 12 hours
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => navigate('/admin/sessions')}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              <BarChart3 className="w-5 h-5" />
              <span>View Sessions</span>
            </button>
            <button
              onClick={() => navigate('/admin/records')}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              <FileText className="w-5 h-5" />
              <span>View All Records</span>
            </button>
            <button
              onClick={() => navigate('/admin/settings')}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Total Students</p>
                  <p className="text-3xl font-bold text-blue-600">{stats.total_students}</p>
                </div>
                <Users className="w-12 h-12 text-blue-600 opacity-20" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Instructors</p>
                  <p className="text-3xl font-bold text-green-600">{stats.total_instructors}</p>
                </div>
                <UserPlus className="w-12 h-12 text-green-600 opacity-20" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Attendance Records</p>
                  <p className="text-3xl font-bold text-purple-600">{stats.total_attendance_records}</p>
                </div>
                <BarChart3 className="w-12 h-12 text-purple-600 opacity-20" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Face Registered</p>
                  <p className="text-3xl font-bold text-orange-600">{stats.students_with_face}</p>
                </div>
                <Download className="w-12 h-12 text-orange-600 opacity-20" />
              </div>
            </div>
          </div>
        )}

        {/* Add Instructor Button */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Instructors</h2>
          <button
            onClick={() => setShowAddInstructor(!showAddInstructor)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Add Instructor
          </button>
        </div>

        {/* Add Instructor Form */}
        {showAddInstructor && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Add New Instructor</h3>
            <form onSubmit={handleAddInstructor} className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Username"
                value={instructorFormData.username}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, username: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={instructorFormData.password}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, password: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={instructorFormData.email}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, email: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Full Name"
                value={instructorFormData.name}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, name: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Department"
                value={instructorFormData.department}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, department: e.target.value })}
                className="px-4 py-2 border rounded-lg"
              />
              {/* Multi-Course Input */}
              <div className="col-span-2 border rounded-lg p-4 bg-gray-50">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Courses <span className="text-red-500">*</span>
                </label>
                
                {/* Display added courses */}
                {instructorFormData.courses.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {instructorFormData.courses.map((course, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                      >
                        {course}
                        <button
                          type="button"
                          onClick={() => {
                            const newCourses = instructorFormData.courses.filter((_, i) => i !== index);
                            setInstructorFormData({ ...instructorFormData, courses: newCourses });
                          }}
                          className="ml-2 text-blue-600 hover:text-blue-800 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
                
                {/* Add course input */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Type course name..."
                    value={newCourse}
                    onChange={(e) => setNewCourse(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        if (newCourse.trim()) {
                          setInstructorFormData({
                            ...instructorFormData,
                            courses: [...instructorFormData.courses, newCourse.trim()]
                          });
                          setNewCourse('');
                        }
                      }
                    }}
                    className="flex-1 px-4 py-2 border rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      if (newCourse.trim()) {
                        setInstructorFormData({
                          ...instructorFormData,
                          courses: [...instructorFormData.courses, newCourse.trim()]
                        });
                        setNewCourse('');
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Add Course
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {instructorFormData.courses.length} course(s) added. Press Enter or click "Add Course" to add.
                </p>
              </div>
              <input
                type="text"
                placeholder="Class Year (e.g., 2nd Year)"
                value={instructorFormData.class_year}
                onChange={(e) => setInstructorFormData({ ...instructorFormData, class_year: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              
              {/* Session Type Selection */}
              <div className="col-span-2 border rounded-lg p-4 bg-gray-50">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Session Types <span className="text-red-500">*</span>
                </label>
                <div className="flex space-x-6">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={instructorFormData.lab_session}
                      onChange={(e) => setInstructorFormData({ ...instructorFormData, lab_session: e.target.checked })}
                      className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-gray-700 font-medium">Lab Session</span>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={instructorFormData.theory_session}
                      onChange={(e) => setInstructorFormData({ ...instructorFormData, theory_session: e.target.checked })}
                      className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-gray-700 font-medium">Theory Session</span>
                  </label>
                </div>
                <p className="text-xs text-gray-500 mt-2">Select at least one session type</p>
              </div>
              
              <div className="col-span-2 flex space-x-2">
                <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  Add Instructor
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddInstructor(false)}
                  className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Add Student Form */}
        {showAddStudent && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Add New Student</h3>
            <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Username"
                value={studentFormData.username}
                onChange={(e) => setStudentFormData({ ...studentFormData, username: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={studentFormData.password}
                onChange={(e) => setStudentFormData({ ...studentFormData, password: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={studentFormData.email}
                onChange={(e) => setStudentFormData({ ...studentFormData, email: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Full Name"
                value={studentFormData.name}
                onChange={(e) => setStudentFormData({ ...studentFormData, name: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Student ID"
                value={studentFormData.student_id}
                onChange={(e) => setStudentFormData({ ...studentFormData, student_id: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              />
              <select
                value={studentFormData.year}
                onChange={(e) => setStudentFormData({ ...studentFormData, year: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              >
                <option value="">Select Year Level</option>
                <option value="1st Year">1st Year</option>
                <option value="2nd Year">2nd Year</option>
                <option value="3rd Year">3rd Year</option>
                <option value="4th Year">4th Year</option>
              </select>
              <select
                value={studentFormData.section || ''}
                onChange={(e) => setStudentFormData({ ...studentFormData, section: e.target.value })}
                className="px-4 py-2 border rounded-lg"
                required
              >
                <option value="">Select Section</option>
                <option value="A">Section A</option>
                <option value="B">Section B</option>
                <option value="C">Section C</option>
                <option value="D">Section D</option>
              </select>
              <input
                type="text"
                placeholder="Department"
                value={studentFormData.department}
                onChange={(e) => setStudentFormData({ ...studentFormData, department: e.target.value })}
                className="px-4 py-2 border rounded-lg"
              />
              <div className="flex space-x-2">
                <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  Add
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddStudent(false)}
                  className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Edit Instructor Modal */}
        {editingInstructor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Edit Instructor</h3>
              <form onSubmit={handleUpdateInstructor} className="space-y-4">
                <input
                  type="text"
                  placeholder="Full Name"
                  value={editingInstructor.name}
                  onChange={(e) => setEditingInstructor({ ...editingInstructor, name: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={editingInstructor.email}
                  onChange={(e) => setEditingInstructor({ ...editingInstructor, email: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
                <input
                  type="text"
                  placeholder="Department"
                  value={editingInstructor.department}
                  onChange={(e) => setEditingInstructor({ ...editingInstructor, department: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <div className="flex space-x-2">
                  <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Save
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

        {/* Instructors Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sessions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {instructors.map((instructor) => (
                <tr key={instructor.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{instructor.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{instructor.username}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{instructor.email}</td>
                  <td className="px-6 py-4">
                    {instructor.courses && instructor.courses.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {instructor.courses.map((course: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                            {course}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-400">{instructor.course_name || '-'}</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{instructor.class_year || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-1">
                      {instructor.session_types?.includes('lab') && (
                        <span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">Lab</span>
                      )}
                      {instructor.session_types?.includes('theory') && (
                        <span className="px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">Theory</span>
                      )}
                      {(!instructor.session_types || instructor.session_types.length === 0) && (
                        <span className="text-gray-400 text-xs">None</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${instructor.enabled !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {instructor.enabled !== false ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap space-x-2">
                    <button
                      onClick={() => handleToggleInstructor(instructor.id)}
                      className={`${instructor.enabled !== false ? 'text-orange-600 hover:text-orange-800' : 'text-green-600 hover:text-green-800'}`}
                    >
                      {instructor.enabled !== false ? 'Disable' : 'Enable'}
                    </button>
                    <button
                      onClick={() => setEditingInstructor(instructor)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteInstructor(instructor.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Edit Student Modal */}
        {editingStudent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Edit Student</h3>
              <form onSubmit={handleUpdateStudent} className="space-y-4">
                <input
                  type="text"
                  placeholder="Full Name"
                  value={editingStudent.name}
                  onChange={(e) => setEditingStudent({ ...editingStudent, name: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={editingStudent.email}
                  onChange={(e) => setEditingStudent({ ...editingStudent, email: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
                <input
                  type="text"
                  placeholder="Department"
                  value={editingStudent.department || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, department: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Year"
                  value={editingStudent.year || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, year: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Section"
                  value={editingStudent.section || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, section: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <div className="flex space-x-2">
                  <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Save
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

        {/* Students Table */}
        <div className="flex justify-between items-center mt-8">
          <h2 className="text-2xl font-bold">Students</h2>
          <button
            onClick={() => setShowAddStudent(!showAddStudent)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Add Student
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Face Registered</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {students.map((student) => (
                <tr key={student.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{student.student_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{student.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{student.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                      {student.year_level || '4th Year'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                      {student.section || '4th Year'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{student.department}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${student.face_registered ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {student.face_registered ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${student.enabled !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {student.enabled !== false ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap space-x-2">
                    <button
                      onClick={() => handleToggleStudent(student.id)}
                      className={`${student.enabled !== false ? 'text-orange-600 hover:text-orange-800' : 'text-green-600 hover:text-green-800'}`}
                    >
                      {student.enabled !== false ? 'Disable' : 'Enable'}
                    </button>
                    <button
                      onClick={() => setEditingStudent(student)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
