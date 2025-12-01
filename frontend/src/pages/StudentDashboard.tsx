import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { studentAPI } from '../lib/api';
import { Calendar, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function StudentDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [attendance, setAttendance] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileRes, attendanceRes] = await Promise.all([
        studentAPI.getProfile(),
        studentAPI.getAttendance()
      ]);
      
      setProfile(profileRes.data);
      setAttendance(attendanceRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    }
  };

  return (
    <Layout title="Student Dashboard">
      <div className="space-y-6">
        {/* Profile Card */}
        {profile && (
          <div className="bg-white p-6 rounded-lg shadow">
            <div>
              <h2 className="text-2xl font-bold">{profile.name}</h2>
              <p className="text-gray-600 mt-1">Student ID: {profile.student_id}</p>
              <p className="text-gray-600">{profile.email}</p>
              {profile.department && (
                <p className="text-gray-600">{profile.department} - Year {profile.year}</p>
              )}
              {profile.section && (
                <p className="text-gray-600">Section: {profile.section}</p>
              )}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Attendance</p>
                <p className="text-3xl font-bold text-blue-600">{attendance.length}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-blue-600 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">This Month</p>
                <p className="text-3xl font-bold text-green-600">
                  {attendance.filter(a => {
                    const date = new Date(a.date);
                    const now = new Date();
                    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
                  }).length}
                </p>
              </div>
              <Calendar className="w-12 h-12 text-green-600 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">This Week</p>
                <p className="text-3xl font-bold text-purple-600">
                  {attendance.filter(a => {
                    const date = new Date(a.date);
                    const now = new Date();
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    return date >= weekAgo;
                  }).length}
                </p>
              </div>
              <Calendar className="w-12 h-12 text-purple-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Attendance History */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold">Attendance History</h3>
          </div>
          
          {attendance.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              No attendance records yet
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Session</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {attendance.map((record) => (
                    <tr key={record.id}>
                      <td className="px-6 py-4 whitespace-nowrap">{record.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{record.session_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                          Present
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
