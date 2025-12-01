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
  section_id?: string;
  year?: string;
  course_name?: string;
  session_type?: 'lab' | 'theory';
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

  const handleExportCSV = async () => {
    try {
      const activeFilters: any = {};
      if (filters.start_date) activeFilters.start_date = filters.start_date;
      if (filters.end_date) activeFilters.end_date = filters.end_date;
      if (filters.student_id) activeFilters.student_id = filters.student_id;
      if (filters.session_id) activeFilters.session_id = filters.session_id;
      
      await instructorAPI.exportCSV(activeFilters);
      toast.success('CSV downloaded successfully!');
    } catch (error) {
      toast.error('Failed to export CSV');
      console.error(error);
    }
  };

  const handleExportExcel = async () => {
    try {
      const activeFilters: any = {};
      if (filters.start_date) activeFilters.start_date = filters.start_date;
      if (filters.end_date) activeFilters.end_date = filters.end_date;
      if (filters.student_id) activeFilters.student_id = filters.student_id;
      if (filters.session_id) activeFilters.session_id = filters.session_id;
      
      await instructorAPI.exportExcel(activeFilters);
      toast.success('Excel downloaded successfully!');
    } catch (error) {
      toast.error('Failed to export Excel');
      console.error(error);
    }
  };

  const filteredRecords = records.filter(record =>
    record.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.session_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout title="Attendance Records">
      <div className="space-y-6">
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

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Filters</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Section</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.date}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(record.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{record.student_name}</div>
                          <div className="text-sm text-gray-500">{record.student_id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                            record.status === 'present' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {record.status === 'present' ? 'Present' : 'Absent'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {record.section_id || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {record.year || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {record.course_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {record.session_type ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              record.session_type === 'lab' 
                                ? 'bg-blue-100 text-blue-800' 
                                : 'bg-purple-100 text-purple-800'
                            }`}>
                              {record.session_type === 'lab' ? 'Lab' : 'Theory'}
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
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
