import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { Users, Edit2, Save, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface Instructor {
  id: number;
  username: string;
  name: string;
  email: string;
  course_name: string;
  class_year: string;
  sections: string[];
  session_types: string[];
}

export default function AdminInstructorSections() {
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingSections, setEditingSections] = useState<string[]>([]);

  const availableSections = ['A', 'B', 'C', 'D', 'E', 'F'];

  useEffect(() => {
    loadInstructors();
  }, []);

  const loadInstructors = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getInstructors();
      setInstructors(response.data.instructors);
    } catch (error) {
      toast.error('Failed to load instructors');
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (instructor: Instructor) => {
    setEditingId(instructor.id);
    setEditingSections([...instructor.sections]);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditingSections([]);
  };

  const saveChanges = async (instructorId: number) => {
    try {
      await adminAPI.updateInstructorSections(instructorId, editingSections);
      toast.success('Sections updated successfully');
      setEditingId(null);
      setEditingSections([]);
      loadInstructors();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to update sections');
    }
  };

  const toggleSection = (section: string) => {
    if (editingSections.includes(section)) {
      setEditingSections(editingSections.filter(s => s !== section));
    } else {
      setEditingSections([...editingSections, section]);
    }
  };

  if (loading) {
    return (
      <Layout title="Manage Instructor Sections">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">Loading instructors...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Manage Instructor Sections">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Users className="w-6 h-6" />
            Instructor Section Assignments
          </h2>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">📋 Instructions</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Assign sections to instructors to control which sections they can create sessions for</li>
            <li>• Instructors will only see their assigned sections in the dropdown when creating sessions</li>
            <li>• Multiple sections can be assigned to one instructor</li>
            <li>• Changes take effect immediately</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Instructor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Session Types
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned Sections
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {instructors.map((instructor) => (
                  <tr key={instructor.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {instructor.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          @{instructor.username}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{instructor.course_name}</div>
                      <div className="text-sm text-gray-500">Year {instructor.class_year}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-1">
                        {instructor.session_types.map((type) => (
                          <span
                            key={type}
                            className={`px-2 py-1 text-xs font-medium rounded-full ${
                              type === 'lab'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-purple-100 text-purple-800'
                            }`}
                          >
                            {type}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {editingId === instructor.id ? (
                        <div className="space-y-2">
                          <div className="flex flex-wrap gap-2">
                            {availableSections.map((section) => (
                              <button
                                key={section}
                                onClick={() => toggleSection(section)}
                                className={`px-3 py-1 text-sm rounded-lg border transition ${
                                  editingSections.includes(section)
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                                }`}
                              >
                                Section {section}
                              </button>
                            ))}
                          </div>
                          <div className="text-xs text-gray-500">
                            Selected: {editingSections.length > 0 ? editingSections.join(', ') : 'None'}
                          </div>
                        </div>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {instructor.sections.length > 0 ? (
                            instructor.sections.map((section) => (
                              <span
                                key={section}
                                className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
                              >
                                Section {section}
                              </span>
                            ))
                          ) : (
                            <span className="text-sm text-gray-500 italic">No sections assigned</span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {editingId === instructor.id ? (
                        <div className="flex gap-2">
                          <button
                            onClick={() => saveChanges(instructor.id)}
                            className="flex items-center gap-1 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700"
                          >
                            <Save className="w-4 h-4" />
                            Save
                          </button>
                          <button
                            onClick={cancelEditing}
                            className="flex items-center gap-1 px-3 py-1 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                          >
                            <X className="w-4 h-4" />
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => startEditing(instructor)}
                          className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          <Edit2 className="w-4 h-4" />
                          Edit
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {instructors.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No instructors found. Add instructors first to assign sections.
          </div>
        )}
      </div>
    </Layout>
  );
}