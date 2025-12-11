import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../lib/api';
import { Users, UserPlus, BarChart3, Download, Settings, LogOut } from 'lucide-react';
import toast from 'react-hot-toast';
import { clearAuth } from '../lib/auth';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await adminAPI.getStats();
      setStats(statsRes.data);
    } catch (error: any) {
      toast.error('Failed to load data');
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-blue-600">SmartAttendance Using Face Recognition</h1>
              <p className="text-gray-600">Admin Dashboard</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* View Date and Action Buttons */}
          <div className="flex justify-between items-center">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                View Date
              </label>
              <input
                type="date"
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex space-x-3 bg-blue-600 px-6 py-3 rounded-lg shadow-lg">
              <button
                onClick={() => navigate('/admin/instructors')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition"
              >
                <UserPlus className="w-5 h-5" />
                <span>Manage Instructors</span>
              </button>
              <button
                onClick={() => navigate('/admin/students')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition"
              >
                <Users className="w-5 h-5" />
                <span>Manage Students</span>
              </button>
              <button
                onClick={() => navigate('/admin/records')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition"
              >
                <BarChart3 className="w-5 h-5" />
                <span>View Records</span>
              </button>
              <button
                onClick={() => navigate('/admin/sessions')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition"
              >
                <Settings className="w-5 h-5" />
                <span>Manage Sessions</span>
              </button>
              <button
                onClick={() => navigate('/admin/settings')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition"
              >
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90 mb-1">Total Students</p>
                    <p className="text-4xl font-bold">{stats.total_students}</p>
                  </div>
                  <Users className="w-16 h-16 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90 mb-1">Instructors</p>
                    <p className="text-4xl font-bold">{stats.total_instructors}</p>
                  </div>
                  <UserPlus className="w-16 h-16 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90 mb-1">Attendance Records</p>
                    <p className="text-4xl font-bold">{stats.total_attendance_records}</p>
                  </div>
                  <BarChart3 className="w-16 h-16 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90 mb-1">Face Registered</p>
                    <p className="text-4xl font-bold">{stats.students_with_face}</p>
                  </div>
                  <Download className="w-16 h-16 opacity-30" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
