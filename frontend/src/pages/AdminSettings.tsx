import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { Save, Settings as SettingsIcon, Activity, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AdminSettings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    face_recognition_threshold: 0.60,
    session_timeout_minutes: 120
  });
  
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const [settingsRes, sessionsRes] = await Promise.all([
        adminAPI.getAdminSettings(),
        adminAPI.getActiveSessions()
      ]);
      
      setSettings(settingsRes.data);
      setActiveSessions(sessionsRes.data);
    } catch (error) {
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      setSavingSettings(true);
      await adminAPI.updateAdminSettings(settings);
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSavingSettings(false);
    }
  };

  // Convert minutes to hours for display
  const timeoutHours = Math.floor(settings.session_timeout_minutes / 60);
  const timeoutMinutes = settings.session_timeout_minutes % 60;

  const handleTimeoutChange = (hours: number, minutes: number) => {
    setSettings({
      ...settings,
      session_timeout_minutes: hours * 60 + minutes
    });
  };

  if (loading) {
    return (
      <Layout title="Admin Settings">
        <div className="text-center py-12">Loading settings...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Settings">
      <div className="space-y-6 max-w-4xl">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/admin')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          <h2 className="text-2xl font-bold">Admin Settings</h2>
        </div>

        {/* Recognition Settings */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Face Recognition Settings</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">Recognition Threshold</label>
                <span className="text-sm font-semibold text-blue-600">
                  {(settings.face_recognition_threshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={settings.face_recognition_threshold}
                onChange={(e) => setSettings({...settings, face_recognition_threshold: parseFloat(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-2">
                Higher values = more strict recognition (fewer false positives). 
                Recommended: 60-70% for balanced accuracy.
              </p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">Session Timeout</label>
                <span className="text-sm font-semibold text-blue-600">
                  {timeoutHours}h {timeoutMinutes}m
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Hours</label>
                  <input
                    type="number"
                    min="0"
                    max="24"
                    value={timeoutHours}
                    onChange={(e) => handleTimeoutChange(parseInt(e.target.value) || 0, timeoutMinutes)}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Minutes</label>
                  <input
                    type="number"
                    min="0"
                    max="59"
                    value={timeoutMinutes}
                    onChange={(e) => handleTimeoutChange(timeoutHours, parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
              </div>
              
              <p className="text-xs text-gray-500 mt-2">
                Sessions will automatically end after this duration of inactivity.
                Default: 2 hours (120 minutes).
              </p>
            </div>
          </div>

          <button
            onClick={handleSaveSettings}
            disabled={savingSettings}
            className="mt-6 flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            <span>{savingSettings ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>

        {/* Active Sessions */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold">Active Sessions</h3>
            <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
              {activeSessions.length} Running
            </span>
          </div>
          
          {activeSessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-2 opacity-20" />
              <p>No active sessions at the moment</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeSessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{session.name}</h4>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                      <span>Instructor: {session.instructor_name}</span>
                      {session.section_id && <span>Section: {session.section_id}</span>}
                      <span>Started: {new Date(session.start_time).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">{session.attendance_count}</div>
                    <div className="text-xs text-gray-500">Attendees</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* System Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">ℹ️ Settings Information</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Recognition threshold affects all face recognition operations</li>
            <li>• Session timeout applies to all instructor sessions</li>
            <li>• Active sessions show real-time running attendance sessions</li>
            <li>• Changes take effect immediately after saving</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
