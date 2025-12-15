import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import CameraPreview from '../components/CameraPreview';
import { attendanceAPI } from '../lib/api';
import { ArrowLeft, Users, CheckCircle, XCircle, AlertCircle, PlayCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AttendanceSession() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<any>(null);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [lastResult, setLastResult] = useState<any>(null);
  const [processing, setProcessing] = useState(false);
  const [lastRecognitionTime, setLastRecognitionTime] = useState(0);
  const [showStopConfirmModal, setShowStopConfirmModal] = useState(false);
  const [showEndSessionModal, setShowEndSessionModal] = useState(false);
  const [showRequirementsNotMetModal, setShowRequirementsNotMetModal] = useState(false);
  const [sessionEligibility, setSessionEligibility] = useState<any>(null);
  const [showReopenModal, setShowReopenModal] = useState(false);

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
    
    // Rate limiting: prevent multiple recognitions within 2 seconds (reduced for better responsiveness)
    const now = Date.now();
    if (now - lastRecognitionTime < 2000) {
      console.log('Recognition rate limited - too soon since last attempt');
      return;
    }
    
    setProcessing(true);
    setLastRecognitionTime(now);
    
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

  const handleStopCamera = () => {
    if (!sessionId) return;
    setShowStopConfirmModal(true);
  };

  const confirmStopCamera = async () => {
    if (!sessionId) return;
    
    setShowStopConfirmModal(false);
    
    try {
      const response = await attendanceAPI.markAbsent(sessionId);
      const data = response.data;
      toast.success(`✓ Camera stopped. Marked ${data.absent_count} students as absent. Session ended.`);
      loadSessionData(); // Refresh attendance list to show absent students
      
      // Navigate back to dashboard after stopping
      setTimeout(() => navigate('/instructor'), 2000);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to mark absent students');
    }
  };

  const cancelStopCamera = () => {
    setShowStopConfirmModal(false);
  };

  const handleEndSession = async () => {
    if (!sessionId || !session) return;
    
    try {
      // Check semester eligibility first
      const eligibilityResponse = await attendanceAPI.checkSemesterEligibility({
        course_name: session.course_name || '',
        section_id: session.section_id || '',
        year: session.year || ''
      });
      
      const eligibility = eligibilityResponse.data;
      setSessionEligibility(eligibility);
      
      if (!eligibility.can_end_semester) {
        // Show requirements not met modal
        setShowRequirementsNotMetModal(true);
      } else {
        // Show confirmation modal
        setShowEndSessionModal(true);
      }
    } catch (error: any) {
      toast.error('Failed to check semester eligibility');
    }
  };

  const confirmEndSession = async () => {
    if (!sessionId) return;
    
    setShowEndSessionModal(false);
    
    try {
      await attendanceAPI.endSession(sessionId, 'semester');
      toast.success('Session ended permanently for semester');
      navigate('/instructor');
    } catch (error) {
      toast.error('Failed to end session');
    }
  };

  const cancelEndSession = () => {
    setShowEndSessionModal(false);
  };

  const closeRequirementsNotMetModal = () => {
    setShowRequirementsNotMetModal(false);
    setSessionEligibility(null);
  };

  const handleReopenSession = () => {
    setShowReopenModal(true);
  };

  const confirmReopenSession = async () => {
    if (!sessionId) return;
    
    setShowReopenModal(false);
    
    try {
      await attendanceAPI.instructorReopenSession(parseInt(sessionId));
      toast.success('Session reopened successfully');
      loadSessionData(); // Refresh session data
    } catch (error: any) {
      const errorData = error.response?.data;
      
      if (errorData?.error === 'Time block mismatch') {
        // Show detailed time block error
        toast.error(
          `${errorData.message}\n\nSuggestion: ${errorData.suggestion}`,
          { duration: 6000 }
        );
      } else if (errorData?.error === 'Outside working hours') {
        // Show working hours error
        toast.error(
          `${errorData.message}\n\nWorking Hours: Morning (8:30 AM - 12:30 PM), Afternoon (1:30 PM - 5:30 PM)`,
          { duration: 6000 }
        );
      } else {
        // Generic error
        toast.error(errorData?.message || 'Failed to reopen session');
      }
    }
  };

  const cancelReopenSession = () => {
    setShowReopenModal(false);
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
          
          {session.status === 'stopped_daily' && (
            <div className="flex gap-2">
              <button
                onClick={handleReopenSession}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Reopen Session
              </button>
            </div>
          )}
        </div>

        {/* Session Info */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-2">{session.name}</h2>
          <div className="flex items-center space-x-4 text-gray-600">
            <span>Started: {new Date(session.start_time).toLocaleString()}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              session.status === 'active' 
                ? 'bg-green-100 text-green-800' 
                : session.status === 'stopped_daily'
                ? 'bg-orange-100 text-orange-800'
                : session.status === 'ended_semester'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {session.status === 'active' ? '🟢 Active' :
               session.status === 'stopped_daily' ? '🟠 Stopped (Daily)' :
               session.status === 'ended_semester' ? '🔴 Ended (Semester)' :
               session.status}
            </span>
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span>
                {attendance.filter(a => a.status === 'present').length} present, {' '}
                {attendance.filter(a => a.status === 'absent').length} absent
              </span>
            </div>
          </div>
          
          {/* Status Message for Stopped Sessions */}
          {session.status === 'stopped_daily' && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    Session Stopped for the Day
                  </p>
                  <p className="text-sm text-yellow-700 mt-1">
                    This session can be reopened during its original time period:
                    {session.time_block === 'morning' ? ' Morning (8:30 AM - 12:30 PM)' : ' Afternoon (1:30 PM - 5:30 PM)'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Section */}
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Live Face Recognition</h3>
              <CameraPreview 
                onCapture={handleCapture}
                autoCapture={session.status === 'active'}
                captureInterval={1500}
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

      {/* Stop Camera Confirmation Modal */}
      {showStopConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Stop Camera & End Session
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700 mb-3">
                Are you sure you want to stop the camera and end this session?
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-yellow-800">
                  <strong>⚠️ This action will:</strong>
                </p>
                <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                  <li>• Mark all remaining students as absent</li>
                  <li>• Permanently end the session</li>
                  <li>• Stop face recognition</li>
                  <li>• Return you to the dashboard</li>
                </ul>
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelStopCamera}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmStopCamera}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition"
              >
                Stop Camera & End Session
              </button>
            </div>
          </div>
        </div>
      )}

      {/* End Session Confirmation Modal */}
      {showEndSessionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  End Session Permanently
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700 mb-3">
                Are you sure you want to end this session permanently for the semester?
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-800">
                  <strong>⚠️ This action cannot be undone!</strong>
                </p>
                <p className="text-sm text-red-700 mt-1">
                  The session will be permanently closed and cannot be reopened.
                </p>
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelEndSession}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmEndSession}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                End Session Permanently
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Requirements Not Met Modal */}
      {showRequirementsNotMetModal && sessionEligibility && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Cannot End Session
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700 mb-3">
                You have not fulfilled the requirements to end the session for the semester.
              </p>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-800 font-medium mb-2">
                  ❌ Requirements Not Met:
                </p>
                <ul className="text-sm text-red-700 space-y-1">
                  {sessionEligibility.days_remaining > 0 && (
                    <li>• Need {sessionEligibility.days_remaining} more days (currently {sessionEligibility.days_elapsed} days, need 120+ days)</li>
                  )}
                  {sessionEligibility.sessions_remaining > 0 && (
                    <li>• Need {sessionEligibility.sessions_remaining} more sessions (currently {sessionEligibility.sessions_conducted} sessions, need 8+ sessions)</li>
                  )}
                </ul>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800 font-medium mb-2">
                  📋 Current Progress:
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Time elapsed: {sessionEligibility.months_elapsed} months ({sessionEligibility.days_elapsed} days)</li>
                  <li>• Sessions conducted: {sessionEligibility.sessions_conducted}</li>
                </ul>
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={closeRequirementsNotMetModal}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reopen Session Confirmation Modal */}
      {showReopenModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <PlayCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Reopen Session
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700 mb-3">
                Are you sure you want to reopen session <strong>"{session.name}"</strong>?
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                <p className="text-sm text-green-800">
                  <strong>✅ This will:</strong>
                </p>
                <ul className="text-sm text-green-700 mt-2 space-y-1">
                  <li>• Reactivate the session for attendance taking</li>
                  <li>• Enable the camera for face recognition</li>
                  <li>• Allow you to continue marking attendance</li>
                </ul>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-yellow-800">
                  <strong>⏰ Time Block Restriction:</strong> Sessions can only be reopened during their original time period.
                </p>
                <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                  <li>• Morning sessions: 8:30 AM - 12:30 PM</li>
                  <li>• Afternoon sessions: 1:30 PM - 5:30 PM</li>
                </ul>
                {session.time_block && (
                  <p className="text-sm text-yellow-700 mt-2">
                    <strong>Current session:</strong> {session.time_block} session
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelReopenSession}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmReopenSession}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                Reopen Session
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
