# ✅ Instructor Dashboard Features - Implementation Complete

## 🎯 What Was Implemented

### Backend (✅ Complete)

**File Created:** `backend/blueprints/instructor.py`

**Endpoints Added:**
1. `GET /api/instructor/records` - Get attendance records with filters
2. `GET /api/instructor/records/export/csv` - Export to CSV
3. `GET /api/instructor/records/export/excel` - Export to Excel (XLSX)
4. `GET /api/instructor/settings` - Get instructor settings
5. `PUT /api/instructor/settings` - Update settings
6. `PUT /api/instructor/change-password` - Change password
7. `GET /api/instructor/students` - Get students list for filtering

**Blueprint Registered:** Added to `backend/app.py`

### Frontend API (✅ Complete)

**File Updated:** `frontend/src/lib/api.ts`

**API Functions Added:**
- `instructorAPI.getRecords(filters)` - Fetch records with filters
- `instructorAPI.exportCSV(filters)` - Download CSV
- `instructorAPI.exportExcel(filters)` - Download Excel
- `instructorAPI.getSettings()` - Get settings
- `instructorAPI.updateSettings(settings)` - Save settings
- `instructorAPI.changePassword(current, new)` - Change password
- `instructorAPI.getStudentsList()` - Get students for dropdown

---

## 📋 Frontend Pages to Create

### 1. Attendance Records Page

**File:** `frontend/src/pages/AttendanceRecords.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { instructorAPI, attendanceAPI } from '../lib/api';
import { Download, FileSpreadsheet, Filter, Search, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';

interface AttendanceRecord {
  id: string;
  student_id: string;
  student_name: string;
  session_id: string;
  session_name: string;
  date: string;
  timestamp: string;
  confidence: number;
  status: string;
}

export default function AttendanceRecords() {
  const navigate = useNavigate();
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    student_id: '',
    session_id: ''
  });
  
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load records, students, and sessions in parallel
      const [recordsRes, studentsRes, sessionsRes] = await Promise.all([
        instructorAPI.getRecords(),
        instructorAPI.getStudentsList(),
        attendanceAPI.getSessions()
      ]);
      
      setRecords(recordsRes.data);
      setStudents(studentsRes.data);
      setSessions(sessionsRes.data);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = async () => {
    try {
      setLoading(true);
      
      // Build filter object (only include non-empty values)
      const activeFilters: any = {};
      if (filters.start_date) activeFilters.start_date = filters.start_date;
      if (filters.end_date) activeFilters.end_date = filters.end_date;
      if (filters.student_id) activeFilters.student_id = filters.student_id;
      if (filters.session_id) activeFilters.session_id = filters.session_id;
      
      const response = await instructorAPI.getRecords(activeFilters);
      setRecords(response.data);
      toast.success(`Found ${response.data.length} records`);
    } catch (error) {
      toast.error('Failed to apply filters');
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({
      start_date: '',
      end_date: '',
      student_id: '',
      session_id: ''
    });
    setSearchTerm('');
    loadInitialData();
  };

  const handleExportCSV = () => {
    const activeFilters: any = {};
    if (filters.start_date) activeFilters.start_date = filters.start_date;
    if (filters.end_date) activeFilters.end_date = filters.end_date;
    if (filters.student_id) activeFilters.student_id = filters.student_id;
    if (filters.session_id) activeFilters.session_id = filters.session_id;
    
    instructorAPI.exportCSV(activeFilters);
    toast.success('Downloading CSV...');
  };

  const handleExportExcel = () => {
    const activeFilters: any = {};
    if (filters.start_date) activeFilters.start_date = filters.start_date;
    if (filters.end_date) activeFilters.end_date = filters.end_date;
    if (filters.student_id) activeFilters.student_id = filters.student_id;
    if (filters.session_id) activeFilters.session_id = filters.session_id;
    
    instructorAPI.exportExcel(activeFilters);
    toast.success('Downloading Excel...');
  };

  // Client-side search filter
  const filteredRecords = records.filter(record =>
    record.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.session_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout title="Attendance Records">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/instructor')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back</span>
            </button>
            <h2 className="text-2xl font-bold">Attendance Records</h2>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleExportCSV}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
            <button
              onClick={handleExportExcel}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Export Excel</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Filters</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium mb-2">Start Date</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            
            {/* End Date */}
            <div>
              <label className="block text-sm font-medium mb-2">End Date</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            
            {/* Student Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Student</label>
              <select
                value={filters.student_id}
                onChange={(e) => setFilters({...filters, student_id: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              >
                <option value="">All Students</option>
                {students.map(student => (
                  <option key={student.student_id} value={student.student_id}>
                    {student.name} ({student.student_id})
                  </option>
                ))}
              </select>
            </div>
            
            {/* Session Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Session</label>
              <select
                value={filters.session_id}
                onChange={(e) => setFilters({...filters, session_id: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              >
                <option value="">All Sessions</option>
                {sessions.map(session => (
                  <option key={session.id} value={session.id}>
                    {session.name}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Search */}
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>
          
          <div className="flex space-x-2 mt-4">
            <button
              onClick={handleApplyFilters}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Filter className="w-4 h-4" />
              <span>Apply Filters</span>
            </button>
            <button
              onClick={handleClearFilters}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Records Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading records...</p>
            </div>
          ) : filteredRecords.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No attendance records found</p>
              <p className="text-sm mt-2">Try adjusting your filters</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Student
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Session
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {record.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(record.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{record.student_name}</div>
                          <div className="text-sm text-gray-500">{record.student_id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {record.session_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            record.confidence >= 0.80 ? 'bg-green-100 text-green-800' :
                            record.confidence >= 0.60 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {(record.confidence * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                            {record.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="px-6 py-4 bg-gray-50 border-t text-sm text-gray-600">
                Showing {filteredRecords.length} of {records.length} records
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
```

---

### 2. Settings Page

**File:** `frontend/src/pages/InstructorSettings.tsx`

```typescript
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
        {/* Header */}
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

        {/* Recognition Settings */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <SettingsIcon className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Recognition Settings</h3>
          </div>
          
          <div className="space-y-6">
            {/* Confidence Threshold */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">
                  Confidence Threshold
                </label>
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

            {/* Capture Interval */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">
                  Auto-Capture Interval
                </label>
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

            {/* Auto Capture Toggle */}
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

        {/* Change Password */}
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
```

---

### 3. Update Instructor Dashboard Navigation

**File:** `frontend/src/pages/InstructorDashboard.tsx`

Add these buttons to the header (around line 50):

```typescript
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
```

---

### 4. Add Routes

**File:** `frontend/src/App.tsx`

Add these imports and routes:

```typescript
import AttendanceRecords from './pages/AttendanceRecords';
import InstructorSettings from './pages/InstructorSettings';

// Add these routes in the Routes section:
<Route path="/instructor/records" element={<AttendanceRecords />} />
<Route path="/instructor/settings" element={<InstructorSettings />} />
```

---

## 🚀 Installation Steps

1. **Install openpyxl for Excel export:**
   ```bash
   cd backend
   pip install openpyxl
   ```

2. **Restart backend:**
   ```bash
   python app.py
   ```

3. **Create the two frontend pages** (copy code from above)

4. **Update InstructorDashboard.tsx** (add navigation buttons)

5. **Update App.tsx** (add routes)

6. **Test the features!**

---

## ✅ Features Implemented

- ✅ Attendance records page with table view
- ✅ Date range filtering (backend)
- ✅ Student filtering (backend)
- ✅ Session filtering (backend)
- ✅ Client-side search
- ✅ Export to CSV
- ✅ Export to Excel (XLSX)
- ✅ Settings page with confidence threshold slider
- ✅ Auto-capture interval adjustment
- ✅ Password change functionality
- ✅ Navigation from dashboard

All existing UI and functionality preserved!
