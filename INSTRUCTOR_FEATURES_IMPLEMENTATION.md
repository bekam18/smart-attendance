# 🎓 Instructor Dashboard - Complete Implementation Guide

## 📊 Current Status

### ✅ Already Working Features
1. **Login System** - Fully functional
2. **Session Management** - Create, start, end sessions
3. **Live Face Recognition** - Real-time webcam capture and recognition
4. **Attendance Recording** - Saves to MongoDB with duplicate prevention
5. **Live Attendance List** - Updates dynamically during session
6. **Session History** - View past sessions

### 🔧 Features to Implement

Based on your requirements, here's what needs to be added:

1. **Attendance Records Page** - View/filter/export all attendance
2. **Settings Page** - Password change, threshold adjustment
3. **Enhanced Unknown Face Handling** - Already working, just needs UI polish

---

## 🚀 Implementation Steps

### Step 1: Backend - Add Instructor Blueprint

Create `backend/blueprints/instructor.py`:

```python
"""
Instructor-specific endpoints for settings and records management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
from utils.security import role_required, hash_password, verify_password
from db.mongo import get_db
import csv
import io

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/settings', methods=['GET'])
@jwt_required()
@role_required('instructor')
def get_settings():
    """Get instructor settings"""
    user_id = get_jwt_identity()
    db = get_db()
    
    settings = db.user_settings.find_one({'user_id': user_id})
    
    if not settings:
        # Return defaults
        return jsonify({
            'confidence_threshold': 0.60,
            'capture_interval': 2,
            'auto_capture': True
        }), 200
    
    return jsonify({
        'confidence_threshold': settings.get('confidence_threshold', 0.60),
        'capture_interval': settings.get('capture_interval', 2),
        'auto_capture': settings.get('auto_capture', True)
    }), 200


@instructor_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required('instructor')
def update_settings():
    """Update instructor settings"""
    user_id = get_jwt_identity()
    data = request.get_json()
    db = get_db()
    
    settings_doc = {
        'user_id': user_id,
        'confidence_threshold': float(data.get('confidence_threshold', 0.60)),
        'capture_interval': int(data.get('capture_interval', 2)),
        'auto_capture': bool(data.get('auto_capture', True)),
        'updated_at': datetime.utcnow()
    }
    
    db.user_settings.update_one(
        {'user_id': user_id},
        {'$set': settings_doc},
        upsert=True
    )
    
    return jsonify({'message': 'Settings updated successfully'}), 200


@instructor_bp.route('/change-password', methods=['PUT'])
@jwt_required()
@role_required('instructor')
def change_password():
    """Change instructor password"""
    user_id = get_jwt_identity()
    data = request.get_json()
    db = get_db()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Both current and new password required'}), 400
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    
    if not verify_password(current_password, user['password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password': hash_password(new_password)}}
    )
    
    return jsonify({'message': 'Password changed successfully'}), 200


@instructor_bp.route('/records', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_attendance_records():
    """Get attendance records with filtering"""
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    student_id = request.args.get('student_id')
    session_id = request.args.get('session_id')
    
    # Build query
    query = {}
    
    # Filter by instructor's sessions only
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if user['role'] == 'instructor':
        instructor_sessions = db.sessions.find({'instructor_id': user_id})
        session_ids = [str(s['_id']) for s in instructor_sessions]
        query['session_id'] = {'$in': session_ids}
    
    # Date range filter
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        if date_query:
            query['date'] = date_query
    
    # Student filter
    if student_id:
        query['student_id'] = student_id
    
    # Session filter
    if session_id:
        query['session_id'] = session_id
    
    # Get records
    records = db.attendance.find(query).sort('timestamp', -1).limit(1000)
    
    result = []
    for record in records:
        student = db.students.find_one({'student_id': record['student_id']})
        session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
        
        result.append({
            'id': str(record['_id']),
            'student_id': record['student_id'],
            'student_name': student['name'] if student else 'Unknown',
            'session_id': record['session_id'],
            'session_name': session['name'] if session else 'Unknown',
            'date': record['date'],
            'timestamp': record['timestamp'].isoformat(),
            'confidence': record.get('confidence', 0),
            'status': record.get('status', 'present')
        })
    
    return jsonify(result), 200


@instructor_bp.route('/records/export', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def export_attendance():
    """Export attendance records to CSV"""
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get same filters as records endpoint
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    student_id = request.args.get('student_id')
    session_id = request.args.get('session_id')
    
    # Build query (same as get_attendance_records)
    query = {}
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if user['role'] == 'instructor':
        instructor_sessions = db.sessions.find({'instructor_id': user_id})
        session_ids = [str(s['_id']) for s in instructor_sessions]
        query['session_id'] = {'$in': session_ids}
    
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        if date_query:
            query['date'] = date_query
    
    if student_id:
        query['student_id'] = student_id
    if session_id:
        query['session_id'] = session_id
    
    # Get records
    records = db.attendance.find(query).sort('timestamp', -1)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Time', 'Student ID', 'Student Name', 'Session', 'Confidence', 'Status'])
    
    # Write data
    for record in records:
        student = db.students.find_one({'student_id': record['student_id']})
        session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
        
        writer.writerow([
            record['date'],
            record['timestamp'].strftime('%H:%M:%S'),
            record['student_id'],
            student['name'] if student else 'Unknown',
            session['name'] if session else 'Unknown',
            f"{record.get('confidence', 0):.2%}",
            record.get('status', 'present')
        ])
    
    # Return CSV
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=attendance_{datetime.now().strftime("%Y%m%d")}.csv'
    }
```

**Register in `backend/app.py`:**

```python
from blueprints.instructor import instructor_bp

app.register_blueprint(instructor_bp, url_prefix='/api/instructor')
```

---

### Step 2: Frontend - Add API Calls

Update `frontend/src/lib/api.ts`:

```typescript
// Instructor API
export const instructorAPI = {
  getSettings: () =>
    api.get('/api/instructor/settings'),
  
  updateSettings: (settings: any) =>
    api.put('/api/instructor/settings', settings),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.put('/api/instructor/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    }),
  
  getRecords: (filters?: any) =>
    api.get('/api/instructor/records', { params: filters }),
  
  exportRecords: (filters?: any) => {
    const params = new URLSearchParams(filters).toString();
    window.open(`${API_URL}/api/instructor/records/export?${params}`, '_blank');
  }
};
```

---

### Step 3: Frontend - Attendance Records Page

Create `frontend/src/pages/AttendanceRecords.tsx`:

```typescript
import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { instructorAPI } from '../lib/api';
import { Download, Filter, Search } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AttendanceRecords() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    student_id: '',
    session_id: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    try {
      setLoading(true);
      const response = await instructorAPI.getRecords(filters);
      setRecords(response.data);
    } catch (error) {
      toast.error('Failed to load records');
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = () => {
    loadRecords();
  };

  const handleExport = () => {
    instructorAPI.exportRecords(filters);
    toast.success('Exporting attendance records...');
  };

  const filteredRecords = records.filter(record =>
    record.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.session_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout title="Attendance Records">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Attendance Records</h2>
          <button
            onClick={handleExport}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Download className="w-5 h-5" />
            <span>Export CSV</span>
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Start Date</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">End Date</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Student name or ID..."
                  className="w-full pl-10 pr-4 py-2 border rounded-lg"
                />
              </div>
            </div>
            <div className="flex items-end">
              <button
                onClick={handleFilter}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Filter className="w-4 h-4" />
                <span>Apply Filters</span>
              </button>
            </div>
          </div>
        </div>

        {/* Records Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : filteredRecords.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No attendance records found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Session</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{record.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium">{record.student_name}</div>
                          <div className="text-sm text-gray-500">{record.student_id}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{record.session_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {(record.confidence * 100).toFixed(1)}%
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
          )}
        </div>

        <div className="text-sm text-gray-500 text-center">
          Showing {filteredRecords.length} of {records.length} records
        </div>
      </div>
    </Layout>
  );
}
```

---

### Step 4: Frontend - Settings Page

Create `frontend/src/pages/InstructorSettings.tsx`:

```typescript
import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { instructorAPI } from '../lib/api';
import { Save, Lock } from 'lucide-react';
import toast from 'react-hot-toast';

export default function InstructorSettings() {
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

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await instructorAPI.getSettings();
      setSettings(response.data);
    } catch (error) {
      toast.error('Failed to load settings');
    }
  };

  const handleSaveSettings = async () => {
    try {
      setLoading(true);
      await instructorAPI.updateSettings(settings);
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setLoading(false);
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
      setLoading(true);
      await instructorAPI.changePassword(passwords.current, passwords.new);
      toast.success('Password changed successfully');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Settings">
      <div className="space-y-6 max-w-2xl">
        <h2 className="text-2xl font-bold">Instructor Settings</h2>

        {/* Recognition Settings */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Recognition Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Confidence Threshold: {(settings.confidence_threshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={settings.confidence_threshold}
                onChange={(e) => setSettings({...settings, confidence_threshold: parseFloat(e.target.value)})}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Higher values = more strict recognition (fewer false positives)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Auto-Capture Interval: {settings.capture_interval} seconds
              </label>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={settings.capture_interval}
                onChange={(e) => setSettings({...settings, capture_interval: parseInt(e.target.value)})}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Time between automatic face captures during active sessions
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="auto_capture"
                checked={settings.auto_capture}
                onChange={(e) => setSettings({...settings, auto_capture: e.target.checked})}
                className="w-4 h-4"
              />
              <label htmlFor="auto_capture" className="text-sm font-medium">
                Enable automatic face capture
              </label>
            </div>
          </div>

          <button
            onClick={handleSaveSettings}
            disabled={loading}
            className="mt-6 flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{loading ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>

        {/* Change Password */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Change Password</h3>
          
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Current Password</label>
              <input
                type="password"
                value={passwords.current}
                onChange={(e) => setPasswords({...passwords, current: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">New Password</label>
              <input
                type="password"
                value={passwords.new}
                onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
                required
                minLength={6}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Confirm New Password</label>
              <input
                type="password"
                value={passwords.confirm}
                onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
                required
                minLength={6}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              <Lock className="w-4 h-4" />
              <span>{loading ? 'Changing...' : 'Change Password'}</span>
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}
```

---

### Step 5: Add Navigation to Dashboard

Update `frontend/src/pages/InstructorDashboard.tsx` - Add buttons in header:

```typescript
<div className="flex justify-between items-center">
  <h2 className="text-2xl font-bold">Attendance Sessions</h2>
  <div className="flex space-x-2">
    <button
      onClick={() => navigate('/instructor/records')}
      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
    >
      View Records
    </button>
    <button
      onClick={() => navigate('/instructor/settings')}
      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
    >
      Settings
    </button>
    <button
      onClick={() => setShowCreateSession(!showCreateSession)}
      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      <PlayCircle className="w-5 h-5" />
      <span>Start New Session</span>
    </button>
  </div>
</div>
```

---

### Step 6: Add Routes

Update `frontend/src/App.tsx`:

```typescript
import AttendanceRecords from './pages/AttendanceRecords';
import InstructorSettings from './pages/InstructorSettings';

// Add routes:
<Route path="/instructor/records" element={<AttendanceRecords />} />
<Route path="/instructor/settings" element={<InstructorSettings />} />
```

---

## ✅ Testing Checklist

1. **Records Page**
   - [ ] View all attendance records
   - [ ] Filter by date range
   - [ ] Search by student name/ID
   - [ ] Export to CSV works
   - [ ] Pagination/scrolling works

2. **Settings Page**
   - [ ] Load current settings
   - [ ] Adjust confidence threshold
   - [ ] Adjust capture interval
   - [ ] Toggle auto-capture
   - [ ] Save settings successfully
   - [ ] Change password works
   - [ ] Password validation works

3. **Integration**
   - [ ] Navigation from dashboard works
   - [ ] Settings apply to recognition
   - [ ] Records show real data
   - [ ] Export includes filtered data

---

## 🎯 Summary

This implementation adds:
- ✅ Complete attendance records management
- ✅ CSV export functionality
- ✅ Instructor settings page
- ✅ Password change functionality
- ✅ Confidence threshold adjustment
- ✅ Auto-capture interval control

All while keeping existing UI and functionality intact!
