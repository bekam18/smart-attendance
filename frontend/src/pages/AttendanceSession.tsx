import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import CameraPreview from '../components/CameraPreview';
import { attendanceAPI } from '../lib/api';
import { ArrowLeft, Users, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AttendanceSession() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<any>(null);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [lastResult, setLastResult] = useState<any>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadSessionData();
    }
  }, [sessionId]);

  const loadSessionData = async () => {
    try {
      const response = await attendanceAPI.getSessionAttendance(sessionId!);
      setSession(response.data.session);
      setAttendance(response.data.attendance);
    } catch (error) {
      toast.error('Failed to load session data');
    }
  };

  const handleCapture = async (blob: Blob) => {
    if (processing || !sessionId) return;
    
    setProcessing(true);
    
    try {
      const response = await attendanceAPI.recognize(blob, sessionId);
      const result = response.data;
      
      setLastResult(result);
      
      if (result.status === 'recognized') {
        toast.success(`✓ ${result.student_name} - Attendance recorded`);
        loadSessionData(); // Refresh attendance list
      } else if (result.status === 'already_marked') {
        toast(`ℹ️ ${result.message}`, { icon: '🔵' });
      } else if (result.status === 'wrong_section') {
        toast.error(`❌ ${result.message}`);
      } else if (result.status === 'unknown') {
        toast.error('❌ Unknown student');
      } else if (result.status === 'no_face') {
        toast('⚠️ No face detected - Please face the camera', { 
          icon: '👤',
          duration: 2000 
        });
      } else if (result.error) {
        toast.error(result.error);
      }
    } catch (error: any) {
      toast.error('Recognition failed');
      console.error(error);
    } finally {
      setProcessing(false);
    }
  };

  const handleStopCamera = async () => {
    if (!sessionId) return;
    
    try {
      const response = await attendanceAPI.markAbsent(sessionId);
      const data = response.data;
      toast.success(`✓ Camera stopped. Marked ${data.absent_count} students as absent`);
      loadSessionData(); // Refresh attendance list to show absent students
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to mark absent students');
    }
  };

  const handleEndSession = async () => {
    if (!sessionId) return;
    
    try {
      await attendanceAPI.endSession(sessionId);
      toast.success('Session ended');
      navigate('/instructor');
    } catch (error) {
      toast.error('Failed to end session');
    }
  };

  if (!session) {
    return (
      <Layout title="Loading...">
        <div className="text-center py-12">Loading session...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Attendance Session">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/instructor')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          
          {session.status === 'active' && (
            <div className="flex gap-2">
              <button
                onClick={handleStopCamera}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
              >
                Stop Camera
              </button>
              <button
                onClick={handleEndSession}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                End Session
              </button>
            </div>
          )}
        </div>

        {/* Session Info */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-2">{session.name}</h2>
          <div className="flex items-center space-x-4 text-gray-600">
            <span>Started: {new Date(session.start_time).toLocaleString()}</span>
            <span className={`px-2 py-1 rounded-full text-xs ${
              session.status === 'active' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {session.status}
            </span>
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span>
                {attendance.filter(a => a.status === 'present').length} present, {' '}
                {attendance.filter(a => a.status === 'absent').length} absent
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Section */}
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Live Face Recognition</h3>
              <CameraPreview 
                onCapture={handleCapture}
                autoCapture={session.status === 'active'}
                captureInterval={2000}
              />
              
              {processing && (
                <div className="mt-4 text-center text-blue-600">
                  Processing...
                </div>
              )}
              
              {/* Last Result */}
              {lastResult && (
                <div className={`mt-4 p-4 rounded-lg ${
                  lastResult.status === 'recognized' ? 'bg-green-50 border border-green-200' :
                  lastResult.status === 'already_marked' ? 'bg-blue-50 border border-blue-200' :
                  lastResult.status === 'wrong_section' ? 'bg-orange-50 border border-orange-200' :
                  lastResult.status === 'unknown' ? 'bg-red-50 border border-red-200' :
                  'bg-yellow-50 border border-yellow-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    {lastResult.status === 'recognized' && <CheckCircle className="w-5 h-5 text-green-600" />}
                    {lastResult.status === 'already_marked' && <AlertCircle className="w-5 h-5 text-blue-600" />}
                    {lastResult.status === 'wrong_section' && <XCircle className="w-5 h-5 text-orange-600" />}
                    {lastResult.status === 'unknown' && <XCircle className="w-5 h-5 text-red-600" />}
                    {lastResult.status === 'no_face' && <AlertCircle className="w-5 h-5 text-yellow-600" />}
                    
                    <div>
                      {lastResult.student_name && (
                        <p className="font-semibold">{lastResult.student_name}</p>
                      )}
                      <p className="text-sm">{lastResult.message || lastResult.status}</p>
                      {lastResult.confidence && (
                        <p className="text-xs text-gray-600">
                          Confidence: {(lastResult.confidence * 100).toFixed(1)}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Attendance List */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Attendance List</h3>
              {attendance.length > 0 && (
                <div className="flex gap-4 text-sm">
                  <span className="text-green-600 font-medium">
                    ✓ {attendance.filter(a => a.status === 'present').length} Present
                  </span>
                  <span className="text-red-600 font-medium">
                    ✗ {attendance.filter(a => a.status === 'absent').length} Absent
                  </span>
                </div>
              )}
            </div>
            
            {attendance.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No attendance recorded yet
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {attendance.map((record, index) => (
                  <div key={index} className={`flex items-center justify-between p-3 rounded-lg ${
                    record.status === 'absent' ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
                  }`}>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        record.status === 'absent' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {record.status === 'absent' ? '🔴 Absent' : '🟢 Present'}
                      </span>
                      <div>
                        <p className="font-medium">{record.student_name}</p>
                        <p className="text-sm text-gray-600">{record.student_id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {record.status === 'present' && (
                        <>
                          <p className="text-sm text-gray-600">
                            {new Date(record.timestamp).toLocaleTimeString()}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(record.confidence * 100).toFixed(1)}%
                          </p>
                        </>
                      )}
                      {record.status === 'absent' && (
                        <p className="text-sm text-red-600">Not present</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
