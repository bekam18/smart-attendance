import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../lib/api';
import { ArrowLeft, RefreshCw, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

interface Session {
  id: number;
  instructor_name: string;
  course_name: string;
  section_id: string;
  year: string;
  session_type: string;
  time_block: string;
  start_time: string;
  end_time?: string;
  status: string;
  attendance_count: number;
}

export default function AdminSessions() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      console.log('🔍 Loading sessions...');
      const response = await adminAPI.getAllSessions();
      console.log('📊 Sessions response:', response.data);
      
      const sessionsList = response.data.sessions || response.data || [];
      console.log('📋 Sessions list:', sessionsList);
      
      setSessions(sessionsList);
      
      if (sessionsList.length === 0) {
        console.log('⚠️ No sessions found in response');
      } else {
        console.log(`✅ Loaded ${sessionsList.length} sessions`);
      }
    } catch (error: any) {
      console.error('❌ Failed to load sessions:', error);
      console.error('Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      toast.error(`Failed to load sessions: ${error.response?.data?.message || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReopenSession = async (sessionId: number, sessionName: string) => {
    if (!confirm(`Are you sure you want to reopen session "${sessionName}"? This will allow the instructor to continue taking attendance.`)) {
      return;
    }

    try {
      const response = await adminAPI.adminReopenSession(sessionId);
      toast.success('Session reopened successfully');
      loadSessions(); // Refresh the list
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to reopen session');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Active
          </span>
        );
      case 'stopped_daily':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3 mr-1" />
            Stopped Daily
          </span>
        );
      case 'ended_semester':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Ended Semester
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };

  const filteredSessions = sessions.filter(session => {
    if (filter === 'all') return true;
    return session.status === filter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/admin')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Session Management</h1>
                <p className="text-gray-600">Manage and reopen sessions</p>
              </div>
            </div>
            <button
              onClick={loadSessions}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              All Sessions ({sessions.length})
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'active'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Active ({sessions.filter(s => s.status === 'active').length})
            </button>
            <button
              onClick={() => setFilter('stopped_daily')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'stopped_daily'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Stopped Daily ({sessions.filter(s => s.status === 'stopped_daily').length})
            </button>
            <button
              onClick={() => setFilter('ended_semester')}
              className={`px-4 py-2 rounded-lg transition ${
                filter === 'ended_semester'
                  ? 'bg-red-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Ended Semester ({sessions.filter(s => s.status === 'ended_semester').length})
            </button>
          </div>
        </div>

        {/* Sessions Table */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading sessions...</p>
            </div>
          ) : filteredSessions.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">No sessions found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Session Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Instructor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Attendance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredSessions.map((session) => (
                    <tr key={session.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {session.course_name || 'No Course'} - {session.session_type}
                          </div>
                          <div className="text-sm text-gray-500">
                            Section {session.section_id}, Year {session.year} - {session.time_block}
                          </div>
                          <div className="text-xs text-gray-400">
                            Started: {new Date(session.start_time).toLocaleString()}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{session.instructor_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(session.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{session.attendance_count} students</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {session.status === 'ended_semester' && (
                          <button
                            onClick={() => handleReopenSession(session.id, `${session.course_name} - ${session.session_type}`)}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            Reopen Session
                          </button>
                        )}
                        {session.status === 'stopped_daily' && (
                          <span className="text-gray-500 text-sm">Can reopen after 12h</span>
                        )}
                        {session.status === 'active' && (
                          <span className="text-green-600 text-sm">Currently active</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">Session Status Guide</h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Active:</strong> Session is currently running, camera can be used</li>
                  <li><strong>Stopped Daily:</strong> Session stopped for the day, can be reopened by instructor after 12 hours</li>
                  <li><strong>Ended Semester:</strong> Session permanently ended by instructor, only admin can reopen</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}