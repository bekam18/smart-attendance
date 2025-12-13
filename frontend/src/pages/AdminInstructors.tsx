import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { UserPlus, Edit2, Trash2, Power, PowerOff, ArrowLeft, BookOpen, GraduationCap } from 'lucide-react';
import toast from 'react-hot-toast';

// Course definitions by year
const COURSES_BY_YEAR = {
  '1': ['Programming Fundamentals', 'Discrete Mathematics', 'Digital Logic', 'English', 'Physics'],
  '2': ['Data Structures', 'Database Systems', 'Computer Architecture', 'Statistics', 'OOP'],
  '3': ['Algorithms', 'Operating Systems', 'Computer Networks', 'Software Engineering', 'Web Development'],
  '4': ['Web', 'AI', 'Java', 'Compiler', 'OS', 'Mobile Development', 'Cloud Computing']
};

interface Instructor {
  id: string;
  username: string;
  name: string;
  email: string;
  department: string;
  courses: string[];
  sections: string[];
  class_year: string;
  session_types: string[];
  enabled: boolean;
}

export default function AdminInstructors() {
  const navigate = useNavigate();
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingInstructor, setEditingInstructor] = useState<Instructor | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [instructorToDelete, setInstructorToDelete] = useState<{id: string, name: string} | null>(null);
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: '',
    department: '',
    class_year: '1',
    courses: [] as string[],
    sections: [] as string[],
    lab_session: false,
    theory_session: true
  });

  useEffect(() => {
    loadInstructors();
  }, []);

  const loadInstructors = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getInstructors();
      // Extract instructors array from the response
      const instructorsData = response.data.instructors || [];
      setInstructors(instructorsData);
    } catch (error) {
      toast.error('Failed to load instructors');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCourse = (course: string) => {
    if (!formData.courses.includes(course)) {
      setFormData({ ...formData, courses: [...formData.courses, course] });
    }
  };

  const handleRemoveCourse = (course: string) => {
    setFormData({ ...formData, courses: formData.courses.filter(c => c !== course) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.courses.length === 0) {
      toast.error('Please select at least one course');
      return;
    }

    if (!formData.lab_session && !formData.theory_session) {
      toast.error('Please select at least one session type');
      return;
    }

    try {
      if (editingInstructor) {
        await adminAPI.updateInstructor(editingInstructor.id, formData);
        toast.success('Instructor updated successfully');
      } else {
        await adminAPI.addInstructor(formData);
        toast.success('Instructor added successfully');
      }
      
      resetForm();
      loadInstructors();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Operation failed');
    }
  };

  const handleEdit = (instructor: Instructor) => {
    setEditingInstructor(instructor);
    setFormData({
      username: instructor.username,
      password: '',
      email: instructor.email,
      name: instructor.name,
      department: instructor.department,
      class_year: instructor.class_year || '1',
      courses: instructor.courses || [],
      sections: instructor.sections || [],
      lab_session: instructor.session_types?.includes('lab') || false,
      theory_session: instructor.session_types?.includes('theory') || true
    });
    setShowAddForm(true);
  };

  const handleDelete = (id: string, name: string) => {
    setInstructorToDelete({ id, name });
    setShowDeleteModal(true);
  };

  const confirmDeleteInstructor = async () => {
    if (!instructorToDelete) return;
    
    setShowDeleteModal(false);
    
    try {
      await adminAPI.deleteInstructor(instructorToDelete.id);
      toast.success('Instructor deleted successfully');
      loadInstructors();
    } catch (error) {
      toast.error('Failed to delete instructor');
    }
    
    setInstructorToDelete(null);
  };

  const cancelDeleteInstructor = () => {
    setShowDeleteModal(false);
    setInstructorToDelete(null);
  };

  const handleToggle = async (id: string) => {
    try {
      await adminAPI.toggleInstructor(id);
      toast.success('Instructor status updated');
      loadInstructors();
    } catch (error) {
      toast.error('Failed to update instructor status');
    }
  };

  const resetForm = () => {
    setFormData({
      username: '',
      password: '',
      email: '',
      name: '',
      department: '',
      class_year: '1',
      courses: [],
      sections: [],
      lab_session: false,
      theory_session: true
    });
    setShowAddForm(false);
    setEditingInstructor(null);
  };

  const availableCourses = COURSES_BY_YEAR[formData.class_year as keyof typeof COURSES_BY_YEAR] || [];

  return (
    <Layout title="Manage Instructors">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/admin')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back</span>
            </button>
            <h2 className="text-2xl font-bold">Instructors</h2>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <UserPlus className="w-5 h-5" />
            <span>{showAddForm ? 'Cancel' : 'Add Instructor'}</span>
          </button>
        </div>

        {/* Add/Edit Form */}
        {showAddForm && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">
              {editingInstructor ? 'Edit Instructor' : 'Add New Instructor'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Username</label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    required
                    disabled={!!editingInstructor}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Password {editingInstructor && '(leave blank to keep current)'}
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    required={!editingInstructor}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Full Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Department</label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="e.g., Computer Science"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Academic Year</label>
                <select
                  value={formData.class_year}
                  onChange={(e) => setFormData({ ...formData, class_year: e.target.value, courses: [] })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option value="">Select Year</option>
                  <option value="1" disabled>1st Year (Not yet activated)</option>
                  <option value="2" disabled>2nd Year (Not yet activated)</option>
                  <option value="3" disabled>3rd Year (Not yet activated)</option>
                  <option value="4">4th Year</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  ℹ️ Currently only 4th year is available. Other years will be activated soon.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Courses <span className="text-red-500">*</span>
                </label>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    {availableCourses.map((course) => (
                      <button
                        key={course}
                        type="button"
                        onClick={() => handleAddCourse(course)}
                        disabled={formData.courses.includes(course)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                          formData.courses.includes(course)
                            ? 'bg-blue-100 border-blue-300 text-blue-700 cursor-not-allowed'
                            : 'bg-white border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                        }`}
                      >
                        {course}
                      </button>
                    ))}
                  </div>
                  
                  {formData.courses.length > 0 && (
                    <div className="pt-3 border-t">
                      <p className="text-xs font-medium text-gray-600 mb-2">Selected Courses:</p>
                      <div className="flex flex-wrap gap-2">
                        {formData.courses.map((course) => (
                          <span
                            key={course}
                            className="inline-flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-full text-sm"
                          >
                            <span>{course}</span>
                            <button
                              type="button"
                              onClick={() => handleRemoveCourse(course)}
                              className="hover:bg-blue-700 rounded-full p-0.5"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {formData.courses.length === 0 && (
                    <p className="text-sm text-gray-500 italic">No courses selected. Click courses above to add.</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Session Types <span className="text-red-500">*</span>
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.lab_session}
                      onChange={(e) => setFormData({ ...formData, lab_session: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span>Lab Session</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.theory_session}
                      onChange={(e) => setFormData({ ...formData, theory_session: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span>Theory Session</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Assign Sections <span className="text-red-500">*</span>
                </label>
                <div className="border rounded-lg p-4 bg-gray-50">
                  <div className="grid grid-cols-5 gap-3">
                    {['A', 'B', 'C', 'D', 'E'].map((section) => (
                      <label
                        key={section}
                        className="flex items-center space-x-2 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={formData.sections.includes(section)}
                          onChange={(e) => {
                            const newSections = e.target.checked
                              ? [...formData.sections, section]
                              : formData.sections.filter(s => s !== section);
                            setFormData({ ...formData, sections: newSections });
                          }}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm font-medium text-gray-700">
                          Section {section}
                        </span>
                      </label>
                    ))}
                  </div>
                  
                  {formData.sections.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-600 mb-2">Selected Sections:</p>
                      <div className="flex flex-wrap gap-2">
                        {formData.sections.map((section) => (
                          <span
                            key={section}
                            className="inline-flex items-center px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium"
                          >
                            Section {section}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {formData.sections.length === 0 && (
                    <p className="text-sm text-gray-500 italic mt-3">
                      Select one or more sections to assign to this instructor
                    </p>
                  )}
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingInstructor ? 'Update Instructor' : 'Add Instructor'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Instructors List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="text-center py-12">Loading instructors...</div>
          ) : instructors.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <UserPlus className="w-12 h-12 mx-auto mb-2 opacity-20" />
              <p>No instructors found. Add your first instructor above.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Courses</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sessions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {instructors.map((instructor) => (
                    <tr key={instructor.id} className={!instructor.enabled ? 'bg-gray-50 opacity-60' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{instructor.name}</div>
                        <div className="text-sm text-gray-500">{instructor.username}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {instructor.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {instructor.department || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center space-x-1 px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                          <GraduationCap className="w-3 h-3" />
                          <span>Year {instructor.class_year}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {instructor.courses && instructor.courses.length > 0 ? (
                            instructor.courses.map((course, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center space-x-1 px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs"
                              >
                                <BookOpen className="w-3 h-3" />
                                <span>{course}</span>
                              </span>
                            ))
                          ) : (
                            <span className="text-sm text-gray-400">No courses</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex flex-col space-y-1">
                          {instructor.session_types?.includes('lab') && (
                            <span className="text-xs text-gray-600">Lab</span>
                          )}
                          {instructor.session_types?.includes('theory') && (
                            <span className="text-xs text-gray-600">Theory</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          instructor.enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {instructor.enabled ? 'Active' : 'Disabled'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEdit(instructor)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleToggle(instructor.id)}
                            className={instructor.enabled ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'}
                            title={instructor.enabled ? 'Disable' : 'Enable'}
                          >
                            {instructor.enabled ? <PowerOff className="w-4 h-4" /> : <Power className="w-4 h-4" />}
                          </button>
                          <button
                            onClick={() => handleDelete(instructor.id, instructor.name)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Delete Instructor Confirmation Modal */}
      {showDeleteModal && instructorToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Delete Instructor
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700 mb-3">
                Are you sure you want to delete instructor <strong>"{instructorToDelete.name}"</strong>?
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-800">
                  <strong>⚠️ This action cannot be undone!</strong>
                </p>
                <ul className="text-sm text-red-700 mt-2 space-y-1">
                  <li>• All instructor data will be permanently deleted</li>
                  <li>• Associated sessions will remain but lose instructor link</li>
                  <li>• Login access will be immediately revoked</li>
                </ul>
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelDeleteInstructor}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmDeleteInstructor}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                Delete Instructor
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
