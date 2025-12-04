import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { attendanceAPI, instructorAPI } from '../lib/api';
import { PlayCircle, StopCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { Session } from '../types';

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
      setSessions(response.data);
    } catch (error) {
      toast.error('Failed to load sessions');
    }
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    
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
    try {
      await attendanceAPI.endSession(sessionId);
      toast.success('Session ended');
      loadSessions();
    } catch (error) {
      toast.error('Failed to end session');
    }
  };

  return (
    <Layout title="Instructor Dashboard">
      <div className="space-y-6">
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
                {sessionType && !timeBlock && (
                  <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800 font-medium">
                      ⚠️ Please select a time block to continue
                    </p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setTimeBlock('morning')}
                    className={`p-4 border-2 rounded-lg text-center transition ${
                      timeBlock === 'morning'
                        ? 'border-orange-600 bg-orange-50 text-orange-900 ring-2 ring-orange-300'
                        : 'border-gray-300 hover:border-orange-400'
                    }`}
                  >
                    <div className="font-semibold">🌅 Morning</div>
                    <div className="text-xs text-gray-600 mt-1">8:30 AM - 12:00 PM</div>
                    {timeBlock === 'morning' && (
                      <div className="mt-2 text-orange-600">✓ Selected</div>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setTimeBlock('afternoon')}
                    className={`p-4 border-2 rounded-lg text-center transition ${
                      timeBlock === 'afternoon'
                        ? 'border-indigo-600 bg-indigo-50 text-indigo-900 ring-2 ring-indigo-300'
                        : 'border-gray-300 hover:border-indigo-400'
                    }`}
                  >
                    <div className="font-semibold">🌆 Afternoon</div>
                    <div className="text-xs text-gray-600 mt-1">1:30 PM - 5:00 PM</div>
                    {timeBlock === 'afternoon' && (
                      <div className="mt-2 text-indigo-600">✓ Selected</div>
                    )}
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Section <span className="text-red-500">*</span>
                </label>
                <select
                  value={section}
                  onChange={(e) => setSection(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                >
                  <option value="">Select Section...</option>
                  <option value="A">Section A</option>
                  <option value="B">Section B</option>
                  <option value="C">Section C</option>
                  <option value="D">Section D</option>
                </select>
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
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      session.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {session.status}
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
    </Layout>
  );
}
