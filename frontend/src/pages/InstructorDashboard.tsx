import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { attendanceAPI, instructorAPI } from '../lib/api';
import { PlayCircle, StopCircle, Clock, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { Session } from '../types';
import { 
  isWithinWorkingHours, 
  useWorkingHoursStatus, 
  formatTimeUntil, 
  getWorkingHoursStatusColor, 
  getWorkingHoursStatusIcon 
} from '../utils/timeRestrictions';

// Working Hours Indicator Component
function WorkingHoursIndicator() {
  const status = useWorkingHoursStatus();
  
  const statusColor = getWorkingHoursStatusColor(status.allowed);
  const statusIcon = getWorkingHoursStatusIcon(status.allowed);
  
  return (
    <div className={`p-3 rounded-lg border ${statusColor}`}>
      <div className="flex items-center gap-2">
        <span className="text-lg">{statusIcon}</span>
        <div>
          <div className="font-medium">
            {status.allowed ? 'System Active' : 'System Blocked'}
          </div>
          <div className="text-sm">
            {status.message}
          </div>
          {!status.allowed && status.minutes_until_next && (
            <div className="text-xs mt-1">
              Next period in: {formatTimeUntil(status.minutes_until_next)}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-2 text-xs">
        <div className="font-medium">Working Hours:</div>
        <div>Morning: 8:30 AM - 12:30 PM</div>
        <div>Afternoon: 1:30 PM - 5:30 PM</div>
        <div className="text-red-600">Lunch Break: 12:30 PM - 1:30 PM (blocked)</div>
      </div>
    </div>
  );
}

export default function InstructorDashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [courseName, setCourseName] = useState('');
  const [sessionType, setSessionType] = useState<'lab' | 'theory' | ''>('');
  const [timeBlock, setTimeBlock] = useState<'morning' | 'afternoon' | ''>('');
  const [section, setSection] = useState('');
  const [instructorInfo, setInstructorInfo] = useState<any>(null);
  const [showCustomCourse, setShowCustomCourse] = useState(false);
  const [customCourse, setCustomCourse] = useState('');
  const [showEndSessionModal, setShowEndSessionModal] = useState(false);
  const [showRequirementsNotMetModal, setShowRequirementsNotMetModal] = useState(false);
  const [sessionToEnd, setSessionToEnd] = useState<any>(null);
  const [showReopenModal, setShowReopenModal] = useState(false);
  const [sessionToReopen, setSessionToReopen] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadInstructorInfo();
    loadSessions();
  }, []);

  const loadInstructorInfo = async () => {
    try {
      const response = await instructorAPI.getInfo();
      setInstructorInfo(response.data);
    } catch (error) {
      toast.error('Failed to load instructor info');
    }
  };

  const loadSessions = async () => {
    try {
      const response = await attendanceAPI.getSessions();
      // Handle both old format (array) and new format (object with sessions array)
      const sessionsList = response.data.sessions || response.data || [];
      setSessions(sessionsList);
    } catch (error) {
      toast.error('Failed to load sessions');
    }
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check working hours first
    const workingHoursCheck = isWithinWorkingHours();
    if (!workingHoursCheck.allowed) {
      toast.error(`Cannot create session: ${workingHoursCheck.message}`);
      return;
    }
    
    if (!sessionType) {
      toast.error('Please select a session type');
      return;
    }
    
    if (!timeBlock) {
      toast.error('Please select a time block');
      return;
    }
    
    if (!section) {
      toast.error('Please enter a section');
      return;
    }
    
    if (!instructorInfo?.class_year) {
      toast.error('Your year is not set. Please contact admin.');
      return;
    }
    
    if (!instructorInfo?.sections || instructorInfo.sections.length === 0) {
      toast.error('No sections assigned to you. Please contact admin.');
      return;
    }
    
    try {
      const response = await attendanceAPI.startSession({
        name: `${sessionType} - ${timeBlock}`,  // Auto-generate session name
        course: courseName,
        session_type: sessionType,
        time_block: timeBlock,
        section_id: section,
        year: instructorInfo.class_year  // Use instructor's year from profile
      });
      
      toast.success('Session created successfully');
      const sessionId = response.data.session_id;
      
      // Navigate to attendance session page
      navigate(`/instructor/session/${sessionId}`);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to create session');
    }
  };

  const handleEndSession = async (sessionId: string) => {
    // Find the session to get course details
    const session = sessions.find(s => s.id === sessionId);
    if (!session) {
      toast.error('Session not found');
      return;
    }
    
    try {
      // Check semester eligibility first
      const eligibilityResponse = await attendanceAPI.checkSemesterEligibility({
        course_name: session.course || '',
        section_id: session.section_id || '',
        year: session.year || ''
      });
      
      const eligibility = eligibilityResponse.data;
      
      // Store session and eligibility data for modal
      setSessionToEnd({ session, eligibility });
      
      if (!eligibility.can_end_semester) {
        // Show requirements not met modal
        setShowRequirementsNotMetModal(true);
      } else {
        // Show confirmation modal
        setShowEndSessionModal(true);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to end session';
      toast.error(errorMessage);
    }
  };

  const confirmEndSession = async () => {
    if (!sessionToEnd) return;
    
    setShowEndSessionModal(false);
    
    try {
      await attendanceAPI.endSession(sessionToEnd.session.id, 'semester');
      toast.success('Session ended permanently');
      loadSessions();
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to end session';
      toast.error(errorMessage);
    }
    
    setSessionToEnd(null);
  };

  const cancelEndSession = () => {
    setShowEndSessionModal(false);
    setSessionToEnd(null);
  };

  const closeRequirementsNotMetModal = () => {
    setShowRequirementsNotMetModal(false);
    setSessionToEnd(null);
  };

  const handleReopenSession = (session: any) => {
    setSessionToReopen(session);
    setShowReopenModal(true);
  };

  const confirmReopenSession = async () => {
    if (!sessionToReopen) return;
    
    setShowReopenModal(false);
    
    try {
      await attendanceAPI.instructorReopenSession(sessionToReopen.id);
      toast.success('Session reopened successfully');
      loadSessions(); // Refresh the list
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
    
    setSessionToReopen(null);
  };

  const cancelReopenSession = () => {
    setShowReopenModal(false);
    setSessionToReopen(null);
  };

  return (
    <Layout title="Instructor Dashboard">
      <div className="space-y-6">
        {/* Working Hours Status */}
        <WorkingHoursIndicator />
        
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Attendance Sessions</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => navigate('/instructor/records')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              View Records
            </button>
            <button
              onClick={() => navigate('/instructor/reports')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              Download Reports
            </button>
            <button
              onClick={() => navigate('/instructor/settings')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Settings
            </button>
            <button
              onClick={() => setShowCreateSession(!showCreateSession)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <PlayCircle className="w-5 h-5" />
              <span>Start New Session</span>
            </button>
          </div>
        </div>

        {/* Instructor Info Banner */}
        {instructorInfo && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900">{instructorInfo.name}</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Class Year: {instructorInfo.class_year}
                </p>
                
                {/* Display all courses */}
                {instructorInfo.courses && instructorInfo.courses.length > 0 ? (
                  <div className="mt-2">
                    <span className="text-sm font-medium text-blue-700">Courses:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {instructorInfo.courses.map((course: string, index: number) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-200 text-blue-900"
                        >
                          {course}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : instructorInfo.course_name ? (
                  <div className="mt-2">
                    <span className="text-sm font-medium text-blue-700">Course:</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-200 text-blue-900 ml-2">
                      {instructorInfo.course_name}
                    </span>
                  </div>
                ) : null}
              </div>
              <div className="flex gap-2">
                {instructorInfo.session_types?.map((type: string) => (
                  <span 
                    key={type}
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      type === 'lab' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-purple-100 text-purple-800'
                    }`}
                  >
                    {type === 'lab' ? 'Lab Sessions' : 'Theory Sessions'}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Create Session Form */}
        {showCreateSession && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Create New Session</h3>
            <form onSubmit={handleCreateSession} className="space-y-4">
              {/* Session Type Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Type <span className="text-red-500">*</span>
                </label>
                <select
                  value={sessionType}
                  onChange={(e) => setSessionType(e.target.value as 'lab' | 'theory' | '')}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select session type...</option>
                  {instructorInfo?.session_types?.includes('lab') && (
                    <option value="lab">Lab</option>
                  )}
                  {instructorInfo?.session_types?.includes('theory') && (
                    <option value="theory">Theory</option>
                  )}
                </select>
              </div>

              {/* Time Block Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Block <span className="text-red-500">*</span>
                </label>
                {(() => {
                  const currentTimeCheck = isWithinWorkingHours();
                  const currentPeriod = currentTimeCheck.period;
                  
                  return (
                    <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800 font-medium">
                        ℹ️ You can only create sessions for the current time period
                      </p>
                      <p className="text-xs text-blue-600 mt-1">
                        Current period: <strong>{currentPeriod === 'morning' ? 'Morning (8:30 AM - 12:30 PM)' : 'Afternoon (1:30 PM - 5:30 PM)'}</strong>
                      </p>
                    </div>
                  );
                })()}
                {sessionType && !timeBlock && (
                  <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800 font-medium">
                      ⚠️ Please select a time block to continue
                    </p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3">
                  {(() => {
                    const currentTimeCheck = isWithinWorkingHours();
                    const currentPeriod = currentTimeCheck.period;
                    const isMorningAllowed = currentPeriod === 'morning';
                    const isAfternoonAllowed = currentPeriod === 'afternoon';
                    
                    return (
                      <>
                        <button
                          type="button"
                          onClick={() => isMorningAllowed ? setTimeBlock('morning') : toast.error('Morning sessions can only be created during morning hours (8:30 AM - 12:30 PM)')}
                          disabled={!isMorningAllowed}
                          className={`p-4 border-2 rounded-lg text-center transition ${
                            timeBlock === 'morning'
                              ? 'border-orange-600 bg-orange-50 text-orange-900 ring-2 ring-orange-300'
                              : isMorningAllowed
                                ? 'border-gray-300 hover:border-orange-400'
                                : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          <div className="font-semibold">🌅 Morning</div>
                          <div className="text-xs mt-1">8:30 AM - 12:30 PM</div>
                          {timeBlock === 'morning' && (
                            <div className="mt-2 text-orange-600">✓ Selected</div>
                          )}
                          {!isMorningAllowed && (
                            <div className="mt-2 text-red-500 text-xs">❌ Not available now</div>
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={() => isAfternoonAllowed ? setTimeBlock('afternoon') : toast.error('Afternoon sessions can only be created during afternoon hours (1:30 PM - 5:30 PM)')}
                          disabled={!isAfternoonAllowed}
                          className={`p-4 border-2 rounded-lg text-center transition ${
                            timeBlock === 'afternoon'
                              ? 'border-indigo-600 bg-indigo-50 text-indigo-900 ring-2 ring-indigo-300'
                              : isAfternoonAllowed
                                ? 'border-gray-300 hover:border-indigo-400'
                                : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          <div className="font-semibold">🌆 Afternoon</div>
                          <div className="text-xs mt-1">1:30 PM - 5:30 PM</div>
                          {timeBlock === 'afternoon' && (
                            <div className="mt-2 text-indigo-600">✓ Selected</div>
                          )}
                          {!isAfternoonAllowed && (
                            <div className="mt-2 text-red-500 text-xs">❌ Not available now</div>
                          )}
                        </button>
                      </>
                    );
                  })()}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Section <span className="text-red-500">*</span>
                </label>
                {instructorInfo?.sections && instructorInfo.sections.length > 0 ? (
                  <select
                    value={section}
                    onChange={(e) => setSection(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  >
                    <option value="">Select Section...</option>
                    {instructorInfo.sections.map((sectionId: string) => (
                      <option key={sectionId} value={sectionId}>
                        Section {sectionId}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-500">
                    No sections assigned. Please contact admin to assign sections.
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Course (Optional)
                </label>
                {!showCustomCourse ? (
                  <select
                    value={courseName}
                    onChange={(e) => {
                      if (e.target.value === 'custom') {
                        setShowCustomCourse(true);
                        setCourseName('');
                      } else {
                        setCourseName(e.target.value);
                      }
                    }}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="">Select Course (Optional)</option>
                    {instructorInfo?.courses && instructorInfo.courses.length > 0 ? (
                      instructorInfo.courses.map((course: string, index: number) => (
                        <option key={index} value={course}>{course}</option>
                      ))
                    ) : instructorInfo?.course_name ? (
                      <option value={instructorInfo.course_name}>{instructorInfo.course_name}</option>
                    ) : null}
                    <option value="custom">Custom Course...</option>
                  </select>
                ) : (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Enter custom course"
                      value={customCourse}
                      onChange={(e) => {
                        setCustomCourse(e.target.value);
                        setCourseName(e.target.value);
                      }}
                      className="flex-1 px-4 py-2 border rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        setShowCustomCourse(false);
                        setCustomCourse('');
                        setCourseName('');
                      }}
                      className="px-3 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
                    >
                      Back
                    </button>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Create & Start
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateSession(false);
                    setCourseName('');
                    setSessionType('');
                    setTimeBlock('');
                    setSection('');
                    setShowCustomCourse(false);
                    setCustomCourse('');
                  }}
                  className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Sessions List */}
        <div className="grid gap-4">
          {sessions.map((session) => (
            <div key={session.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-xl font-semibold">{session.name}</h3>
                    {session.session_type && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.session_type === 'lab' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {session.session_type === 'lab' ? 'Lab' : 'Theory'}
                      </span>
                    )}
                    {session.time_block && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.time_block === 'morning' 
                          ? 'bg-orange-100 text-orange-800' 
                          : 'bg-indigo-100 text-indigo-800'
                      }`}>
                        {session.time_block === 'morning' ? '🌅 Morning' : '🌆 Afternoon'}
                      </span>
                    )}
                  </div>
                  {session.course && (
                    <p className="text-gray-600 mt-1">{session.course}</p>
                  )}
                  {(session.section_id || session.year) && (
                    <p className="text-sm text-gray-500 mt-1">
                      {session.section_id && `Section ${session.section_id}`}
                      {session.section_id && session.year && ' • '}
                      {session.year}
                    </p>
                  )}
                  <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(session.start_time).toLocaleString()}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      session.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : (session.status === 'stopped_daily' || session.status === 'completed')
                        ? 'bg-orange-100 text-orange-800'
                        : session.status === 'ended_semester'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {session.status === 'active' ? '🟢 Active' :
                       session.status === 'stopped_daily' ? '🟠 Stopped (Daily)' :
                       session.status === 'completed' ? '🟠 Stopped (Daily)' :
                       session.status === 'ended_semester' ? '🔴 Ended (Semester)' :
                       session.status}
                    </span>
                    <span>Attendance: {session.attendance_count}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  {session.status === 'active' ? (
                    <>
                      <button
                        onClick={() => navigate(`/instructor/session/${session.id}`)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        Open Session
                      </button>
                      <button
                        onClick={() => handleEndSession(session.id)}
                        className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                      >
                        <StopCircle className="w-4 h-4" />
                        <span>End</span>
                      </button>
                    </>
                  ) : (session.status === 'stopped_daily' || session.status === 'completed') ? (
                    <>
                      <button
                        onClick={() => handleReopenSession(session)}
                        className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        <PlayCircle className="w-4 h-4" />
                        <span>Reopen</span>
                      </button>
                      <button
                        onClick={() => navigate(`/instructor/session/${session.id}`)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                      >
                        View Details
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => navigate(`/instructor/session/${session.id}`)}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      View Details
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {sessions.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No sessions yet. Create your first session to start taking attendance.
            </div>
          )}
        </div>
      </div>

      {/* End Session Confirmation Modal */}
      {showEndSessionModal && sessionToEnd && (
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
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-800 font-medium mb-2">
                  ⚠️ This action cannot be undone!
                </p>
              </div>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm text-green-800 font-medium mb-2">
                  ✅ Requirements Met:
                </p>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• {sessionToEnd.eligibility.months_elapsed} months elapsed (need 4+)</li>
                  <li>• {sessionToEnd.eligibility.sessions_conducted} sessions conducted (need 8+)</li>
                </ul>
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
      {showRequirementsNotMetModal && sessionToEnd && (
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
                  {sessionToEnd.eligibility.days_remaining > 0 && (
                    <li>• Need {sessionToEnd.eligibility.days_remaining} more days (currently {sessionToEnd.eligibility.days_elapsed} days, need 120+ days)</li>
                  )}
                  {sessionToEnd.eligibility.sessions_remaining > 0 && (
                    <li>• Need {sessionToEnd.eligibility.sessions_remaining} more sessions (currently {sessionToEnd.eligibility.sessions_conducted} sessions, need 8+ sessions)</li>
                  )}
                </ul>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800 font-medium mb-2">
                  📋 Current Progress:
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Time elapsed: {sessionToEnd.eligibility.months_elapsed} months ({sessionToEnd.eligibility.days_elapsed} days)</li>
                  <li>• Sessions conducted: {sessionToEnd.eligibility.sessions_conducted}</li>
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
      {showReopenModal && sessionToReopen && (
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
                Are you sure you want to reopen session <strong>"{sessionToReopen.course} - {sessionToReopen.session_type}"</strong>?
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                <p className="text-sm text-green-800">
                  <strong>✅ This will:</strong>
                </p>
                <ul className="text-sm text-green-700 mt-2 space-y-1">
                  <li>• Reactivate the session for attendance taking</li>
                  <li>• Allow you to continue using the camera</li>
                  <li>• Enable face recognition for this session</li>
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
                <p className="text-sm text-yellow-700 mt-2">
                  <strong>Current session:</strong> {sessionToReopen.time_block} session
                </p>
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
