import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { studentAPI } from '../lib/api';
import { Calendar, CheckCircle, AlertTriangle, User, BookOpen, GraduationCap, Users } from 'lucide-react';
import toast from 'react-hot-toast';

export default function StudentDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [allAttendance, setAllAttendance] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [courseFilter, setCourseFilter] = useState<string>('');
  const [instructorFilter, setInstructorFilter] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterAttendance();
  }, [courseFilter, instructorFilter, allAttendance]);

  const loadData = async () => {
    try {
      setLoading(true);
      const API_URL = 'http://127.0.0.1:5000';
      const [profileRes, attendanceRes, statsRes] = await Promise.all([
        studentAPI.getProfile(),
        studentAPI.getAttendance(),
        fetch(`${API_URL}/api/students/attendance/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }).then(res => res.json())
      ]);
      
      setProfile(profileRes.data);
      setAllAttendance(attendanceRes.data);
      setAttendance(attendanceRes.data);
      setStats(statsRes);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const filterAttendance = () => {
    let filtered = [...allAttendance];
    
    if (courseFilter) {
      filtered = filtered.filter(record => record.course_name === courseFilter);
    }
    
    if (instructorFilter) {
      filtered = filtered.filter(record => record.instructor_id === parseInt(instructorFilter));
    }
    
    setAttendance(filtered);
  };

  const resetFilters = () => {
    setCourseFilter('');
    setInstructorFilter('');
  };

  if (loading) {
    return (
      <Layout title="Student Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Student Dashboard">
      <div className="space-y-6">
        {/* Profile Card */}
        {profile && (
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-lg shadow-lg">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 p-4 rounded-full">
                  <User className="w-12 h-12" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold">{profile.name}</h2>
                  <p className="text-blue-100 mt-1">Student ID: {profile.student_id}</p>
                  <p className="text-blue-100">{profile.email}</p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <GraduationCap className="w-5 h-5" />
                  <span className="text-sm text-blue-100">Year</span>
                </div>
                <p className="text-xl font-bold mt-1">{profile.year}</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span className="text-sm text-blue-100">Section</span>
                </div>
                <p className="text-xl font-bold mt-1">Section {profile.section}</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <span className="text-sm text-blue-100">Courses</span>
                </div>
                <p className="text-xl font-bold mt-1">{profile.courses?.length || 0}</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span className="text-sm text-blue-100">Instructors</span>
                </div>
                <p className="text-xl font-bold mt-1">{profile.instructors?.length || 0}</p>
              </div>
            </div>
          </div>
        )}

        {/* Courses and Instructors */}
        {profile && (profile.courses?.length > 0 || profile.instructors?.length > 0) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Courses */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2 text-blue-600" />
                My Courses
              </h3>
              {profile.courses && profile.courses.length > 0 ? (
                <ul className="space-y-2">
                  {profile.courses.map((course: string, index: number) => (
                    <li key={index} className="flex items-center space-x-2 p-2 bg-blue-50 rounded">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-700">{course}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No courses assigned</p>
              )}
            </div>

            {/* Instructors */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <User className="w-5 h-5 mr-2 text-purple-600" />
                My Instructors
              </h3>
              {profile.instructors && profile.instructors.length > 0 ? (
                <ul className="space-y-3">
                  {profile.instructors.map((instructor: any) => (
                    <li key={instructor.id} className="p-3 bg-purple-50 rounded">
                      <p className="font-medium text-gray-900">{instructor.name}</p>
                      <p className="text-sm text-gray-600">{instructor.course}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No instructors assigned</p>
              )}
            </div>
          </div>
        )}

        {/* Attendance Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Lab Attendance */}
            <div className={`bg-white p-6 rounded-lg shadow ${stats.lab.warning ? 'border-2 border-red-500' : 'border-2 border-green-500'}`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Lab Attendance</h3>
                {stats.lab.warning && (
                  <AlertTriangle className="w-6 h-6 text-red-500" />
                )}
              </div>
              
              <div className="text-center mb-4">
                <div className={`text-5xl font-bold ${stats.lab.warning ? 'text-red-600' : 'text-green-600'}`}>
                  {stats.lab.percentage}%
                </div>
                <p className="text-gray-600 mt-2">
                  {stats.lab.present} / {stats.lab.total} sessions
                </p>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div 
                  className={`h-3 rounded-full ${stats.lab.warning ? 'bg-red-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(stats.lab.percentage, 100)}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-sm text-gray-600">
                <span>Required: {stats.lab.required}%</span>
                <span className={stats.lab.warning ? 'text-red-600 font-bold' : 'text-green-600'}>
                  {stats.lab.warning ? '⚠️ WARNING' : '✓ Good'}
                </span>
              </div>
              
              {stats.lab.warning && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-800">
                    <strong>Warning:</strong> Your lab attendance is below the required 100%. Please attend all lab sessions.
                  </p>
                </div>
              )}
            </div>

            {/* Theory Attendance */}
            <div className={`bg-white p-6 rounded-lg shadow ${stats.theory.warning ? 'border-2 border-red-500' : 'border-2 border-green-500'}`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Theory Attendance</h3>
                {stats.theory.warning && (
                  <AlertTriangle className="w-6 h-6 text-red-500" />
                )}
              </div>
              
              <div className="text-center mb-4">
                <div className={`text-5xl font-bold ${stats.theory.warning ? 'text-red-600' : 'text-green-600'}`}>
                  {stats.theory.percentage}%
                </div>
                <p className="text-gray-600 mt-2">
                  {stats.theory.present} / {stats.theory.total} sessions
                </p>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div 
                  className={`h-3 rounded-full ${stats.theory.warning ? 'bg-red-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(stats.theory.percentage, 100)}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-sm text-gray-600">
                <span>Required: {stats.theory.required}%</span>
                <span className={stats.theory.warning ? 'text-red-600 font-bold' : 'text-green-600'}>
                  {stats.theory.warning ? '⚠️ WARNING' : '✓ Good'}
                </span>
              </div>
              
              {stats.theory.warning && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-800">
                    <strong>Warning:</strong> Your theory attendance is below the required 80%. Please improve your attendance.
                  </p>
                </div>
              )}
            </div>

            {/* Overall Attendance */}
            <div className="bg-white p-6 rounded-lg shadow border-2 border-blue-500">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Overall Attendance</h3>
                <CheckCircle className="w-6 h-6 text-blue-600" />
              </div>
              
              <div className="text-center mb-4">
                <div className="text-5xl font-bold text-blue-600">
                  {stats.overall.percentage}%
                </div>
                <p className="text-gray-600 mt-2">
                  {stats.overall.present} / {stats.overall.total} sessions
                </p>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div 
                  className="h-3 rounded-full bg-blue-500"
                  style={{ width: `${Math.min(stats.overall.percentage, 100)}%` }}
                ></div>
              </div>
              
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Present:</span>
                  <span className="font-semibold text-green-600">{stats.overall.present}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Absent:</span>
                  <span className="font-semibold text-red-600">{stats.overall.absent}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Attendance</p>
                <p className="text-3xl font-bold text-blue-600">{attendance.length}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-blue-600 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">This Month</p>
                <p className="text-3xl font-bold text-green-600">
                  {attendance.filter(a => {
                    const date = new Date(a.date);
                    const now = new Date();
                    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
                  }).length}
                </p>
              </div>
              <Calendar className="w-12 h-12 text-green-600 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">This Week</p>
                <p className="text-3xl font-bold text-purple-600">
                  {attendance.filter(a => {
                    const date = new Date(a.date);
                    const now = new Date();
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    return date >= weekAgo;
                  }).length}
                </p>
              </div>
              <Calendar className="w-12 h-12 text-purple-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Attendance History */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold flex items-center mb-4">
              <Calendar className="w-5 h-5 mr-2 text-blue-600" />
              Attendance History
            </h3>
            
            {/* Filters */}
            <div className="flex flex-wrap gap-4 items-end">
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Course
                </label>
                <select
                  value={courseFilter}
                  onChange={(e) => setCourseFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Courses</option>
                  {profile?.courses?.map((course: string) => (
                    <option key={course} value={course}>{course}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Instructor
                </label>
                <select
                  value={instructorFilter}
                  onChange={(e) => setInstructorFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Instructors</option>
                  {profile?.instructors?.map((instructor: any) => (
                    <option key={instructor.id} value={instructor.id}>
                      {instructor.name} - {instructor.course}
                    </option>
                  ))}
                </select>
              </div>
              
              {(courseFilter || instructorFilter) && (
                <button
                  onClick={resetFilters}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                >
                  Clear Filters
                </button>
              )}
              
              <div className="text-sm text-gray-600">
                Showing {attendance.length} of {allAttendance.length} records
              </div>
            </div>
          </div>
          
          {attendance.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Calendar className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p className="text-lg">No attendance records yet</p>
              <p className="text-sm mt-2">Your attendance will appear here once sessions begin</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Instructor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Session</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {attendance.map((record) => (
                    <tr key={record.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.course_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.instructor_name || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.session_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          record.session_type === 'lab' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          {record.session_type === 'lab' ? 'Lab' : 'Theory'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          record.status === 'present' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {record.status === 'present' ? 'Present' : 'Absent'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
