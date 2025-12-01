import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { instructorAPI } from '../lib/api';
import { Save, Lock, ArrowLeft, Settings as SettingsIcon } from 'lucide-react';
import toast from 'react-hot-toast';

export default function InstructorSettings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    confidence_threshold: 0.60,
    capture_interval: 2,
    auto_capture: true
  });
  
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await instructorAPI.getSettings();
      setSettings(response.data);
    } catch (error) {
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      setSavingSettings(true);
      await instructorAPI.updateSettings(settings);
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSavingSettings(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwords.new !== passwords.confirm) {
      toast.error('New passwords do not match');
      return;
    }
    
    if (passwords.new.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    
    try {
      setChangingPassword(true);
      await instructorAPI.changePassword(passwords.current, passwords.new);
      toast.success('Password changed successfully');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Settings">
        <div className="text-center py-12">Loading settings...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Settings">
      <div className="space-y-6 max-w-3xl">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/instructor')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          <h2 className="text-2xl font-bold">Instructor Settings</h2>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Recognition Settings</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">Confidence Threshold</label>
                <span className="text-sm font-semibold text-blue-600">
                  {(settings.confidence_threshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={settings.confidence_threshold}
                onChange={(e) => setSettings({...settings, confidence_threshold: parseFloat(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-2">
                Higher values = more strict recognition (fewer false positives). 
                Recommended: 60-70% for balanced accuracy.
              </p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">Auto-Capture Interval</label>
                <span className="text-sm font-semibold text-blue-600">
                  {settings.capture_interval} seconds
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={settings.capture_interval}
                onChange={(e) => setSettings({...settings, capture_interval: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-2">
                Time between automatic face captures during active sessions.
                Lower values = more frequent captures.
              </p>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <label htmlFor="auto_capture" className="text-sm font-medium">
                  Enable Automatic Face Capture
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  Automatically capture and recognize faces during active sessions
                </p>
              </div>
              <input
                type="checkbox"
                id="auto_capture"
                checked={settings.auto_capture}
                onChange={(e) => setSettings({...settings, auto_capture: e.target.checked})}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
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

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <Lock className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Change Password</h3>
          </div>
          
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Current Password</label>
              <input
                type="password"
                value={passwords.current}
                onChange={(e) => setPasswords({...passwords, current: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Enter current password"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">New Password</label>
              <input
                type="password"
                value={passwords.new}
                onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                minLength={6}
                placeholder="Enter new password (min 6 characters)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Confirm New Password</label>
              <input
                type="password"
                value={passwords.confirm}
                onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                minLength={6}
                placeholder="Confirm new password"
              />
            </div>

            <button
              type="submit"
              disabled={changingPassword}
              className="flex items-center space-x-2 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Lock className="w-4 h-4" />
              <span>{changingPassword ? 'Changing...' : 'Change Password'}</span>
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}
