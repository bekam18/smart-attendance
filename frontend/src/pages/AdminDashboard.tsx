import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../lib/api';
import { Users, UserPlus, BarChart3, Download, Settings, LogOut, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { clearAuth } from '../lib/auth';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [sectionAnalytics, setSectionAnalytics] = useState<any[]>([]);
  const [timeBlockAnalytics, setTimeBlockAnalytics] = useState<any[]>([]);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  useEffect(() => {
    loadData();
    loadAnalytics();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await adminAPI.getStats();
      setStats(statsRes.data);
    } catch (error: any) {
      toast.error('Failed to load data');
    }
  };

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      
      console.log('🔍 Loading REAL analytics data from database...');
      
      // Load real analytics data from generated JSON file
      try {
        const response = await fetch('/analytics_data.json');
        if (response.ok) {
          const realData = await response.json();
          
          console.log('✅ Real analytics data loaded:', realData.metadata);
          
          // Use the real data from database
          setSectionAnalytics(realData.section_attendance || []);
          setTimeBlockAnalytics(realData.time_block_analysis || []);
          
          console.log('📊 Analytics data loaded:');
          console.log(`   - Sections: ${realData.section_attendance?.length || 0}`);
          console.log(`   - Time blocks: ${realData.time_block_analysis?.length || 0}`);
          console.log(`   - Generated: ${realData.metadata?.generated_at}`);
          
        } else {
          throw new Error('Failed to load analytics data file');
        }
        
      } catch (fileError) {
        console.error('❌ Failed to load real analytics data:', fileError);
        
        // Fallback: Try API endpoints
        try {
          console.log('🔄 Trying API endpoints as fallback...');
          const [
            sectionRes,
            timeBlockRes
          ] = await Promise.all([
            adminAPI.getSectionAttendanceAnalytics(),
            adminAPI.getTimeBlockAnalysis()
          ]);
          
          setSectionAnalytics(sectionRes.data || []);
          setTimeBlockAnalytics(timeBlockRes.data || []);
          
          console.log('✅ API analytics data loaded successfully');
          
        } catch (apiError) {
          console.error('❌ API endpoints also failed:', apiError);
          // Set empty arrays - no fallback sample data
          setSectionAnalytics([]);
          setTimeBlockAnalytics([]);
        }
      }
      
    } catch (error: any) {
      console.error('Analytics loading error:', error);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
    toast.success('Logged out successfully');
  };

  // Chart colors
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
  
  // Format percentage for display
  const formatPercentage = (value: number) => `${value?.toFixed(1)}%`;
  
  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {typeof entry.name === 'string' && entry.name.includes('percentage') ? '%' : ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
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

          {/* Stats Cards - Original Structure */}
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

          {/* NEW: Analytics Section - Added Below Original Structure */}
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">📊 Attendance Analytics & Reports</h2>
              <p className="text-gray-600">Comprehensive insights into attendance patterns and performance</p>
            </div>

            {analyticsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading analytics...</p>
              </div>
            ) : (
              <>
                {/* Section Attendance & Time Block Analysis */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Section Attendance Pie Chart */}
                  <div className="bg-white p-6 rounded-xl shadow-lg">
                    <div className="flex items-center mb-4">
                      <Users className="w-6 h-6 text-blue-600 mr-2" />
                      <h3 className="text-lg font-semibold">Attendance by Section</h3>
                    </div>
                    {sectionAnalytics.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={sectionAnalytics}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={(entry: any) => 
                              `Section ${entry.section}: ${formatPercentage(entry.attendance_percentage)}`
                            }
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="attendance_percentage"
                          >
                            {sectionAnalytics.map((_entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip content={<CustomTooltip />} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex flex-col items-center justify-center text-gray-500">
                        <BarChart3 className="w-12 h-12 mb-2 opacity-50" />
                        <p className="text-center">No section data available</p>
                        <p className="text-xs text-center mt-1">Data will appear after attendance sessions are conducted</p>
                      </div>
                    )}
                  </div>

                  {/* Time Block Analysis */}
                  <div className="bg-white p-6 rounded-xl shadow-lg">
                    <div className="flex items-center mb-4">
                      <Clock className="w-6 h-6 text-green-600 mr-2" />
                      <h3 className="text-lg font-semibold">Morning vs Afternoon Attendance</h3>
                    </div>
                    {timeBlockAnalytics.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={timeBlockAnalytics}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="time_block" />
                          <YAxis />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Bar dataKey="present_count" fill="#10B981" name="Present" />
                          <Bar dataKey="absent_count" fill="#EF4444" name="Absent" />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center text-gray-500">
                        No time block data available
                      </div>
                    )}
                  </div>
                </div>




              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
