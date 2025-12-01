import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { ArrowLeft, Clock, Users, Filter } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AdminSessions() {
  const navigate = useNavigate();
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [recentSessions, setRecentSessions] = useState<any[]>([]);
  const [instructors, setInstructors] = useState<any[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [filterInstructor, setFilterInstructor] = useState('');
  const [filterCourse, setFilterCourse] = useState('');
  const [filterSessionType, setFilterSessionType] = useState('');
  const [filterTimeBlock, setFilterTimeBlock] = useState('');

  useEffect(() => {
    loadInstructors();
    loadSessions();
  }, []);

  const loadInstructors = async () => {
    try {
      const response = await adminAPI.getInstructors();
      setInstructors(response.data);
    } catch (error) {
      console.error('Failed to load instructors');
    }
  };

  const loadSessions = async () => {
    try {
      const filters: any = {};
      if (filterInstructor) filters.instructor_id = filterInstructor;
      if (filterCourse) filters.course_name = filterCourse;
      if (filterSessionType) filters.session_type = filterSessionType;
      if (filterTimeBlock) filters.time_block = filterTimeBlock;

      const [activeRes, recentRes] = await Promise.all([
        adminAPI.getActiveSessions(filters),
        adminAPI.getRecentSessions(filters)
      ]);
      
      setActiveSessions(activeRes.data);
      setRecentSessions(recentRes.data);
    } catch (error) {
      toast.error('Failed to load sessions');
    }
  };

  const handleApplyFilters = () => {
    loadSessions();
  };

  const handleClearFilters = () => {
    setFilterInstructor('');
    setFilterCourse('');
    setFilterSessionType('');
    setFilterTimeBlock('');
    setTimeout(() => loadSessions(), 100);
  };

  return (
    <Layout title="Session Management">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/admin')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            <Filter className="w-5 h-5" />
            <span>{showFilters ? 'Hide Filters' : 'Show Filters'}</span>
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Filter Sessions</h3>
            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instructor
                </label>
                <select
                  value={filterInstructor}
                  onChange={(e) => setFilterInstructor(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="">All Instructors</option>
                  {instructors.map((instructor) => (
                    <option key={instructor.id} value={instructor.id}>
                      {instructor.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Course
                </label>
                <input
                  type="text"
                  value={filterCourse}
                  onChange={(e) => setFilterCourse(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter course name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Type
                </label>
                <select
                  value={filterSessionType}
                  onChange={(e) => setFilterSessionType(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="">All Types</option>
                  <option value="lab">Lab</option>
                  <option value="theory">Theory</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Block
                </label>
                <select
                  value={filterTimeBlock}
                  onChange={(e) => setFilterTimeBlock(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="">All Time Blocks</option>
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                </select>
              </div>
            </div>
            
            <div className="flex space-x-2 mt-4">
              <button
                onClick={handleApplyFilters}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Apply Filters
              </button>
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}

        {/* Active Sessions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">Active Sessions</h2>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                {activeSessions.length} Active
              </span>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Instructor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section/Year</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time Block</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attendance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {activeSessions.map((session) => (
                  <tr key={session.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">{session.instructor_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{session.course_name || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.session_type === 'lab' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {session.session_type === 'lab' ? 'Lab' : 'Theory'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {session.section_id && `Sec ${session.section_id}`}
                      {session.section_id && session.year && ' • '}
                      {session.year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.time_block === 'morning' 
                          ? 'bg-orange-100 text-orange-800' 
                          : 'bg-indigo-100 text-indigo-800'
                      }`}>
                        {session.time_block === 'morning' ? '🌅 Morning' : '🌆 Afternoon'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(session.start_time).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4 text-gray-500" />
                        <span>{session.attendance_count}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {activeSessions.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No active sessions at the moment
              </div>
            )}
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">Recent Sessions</h2>
              <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                Last {recentSessions.length}
              </span>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Instructor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section/Year</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time Block</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">End Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attendance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {recentSessions.map((session) => (
                  <tr key={session.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">{session.instructor_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{session.course_name || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.session_type === 'lab' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {session.session_type === 'lab' ? 'Lab' : 'Theory'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {session.section_id && `Sec ${session.section_id}`}
                      {session.section_id && session.year && ' • '}
                      {session.year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.time_block === 'morning' 
                          ? 'bg-orange-100 text-orange-800' 
                          : 'bg-indigo-100 text-indigo-800'
                      }`}>
                        {session.time_block === 'morning' ? '🌅 Morning' : '🌆 Afternoon'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(session.start_time).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {session.end_time ? new Date(session.end_time).toLocaleString() : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4 text-gray-500" />
                        <span>{session.attendance_count}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {recentSessions.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No recent sessions found
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
