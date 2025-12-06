import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { instructorAPI } from '../lib/api';
import { Download, FileSpreadsheet, TrendingUp, AlertTriangle, FileText, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import Layout from '../components/Layout';

interface ReportData {
  student_id: string;
  name: string;
  section: string;
  total_sessions: number;
  present_count: number;
  absent_count: number;
  percentage: number;
  lab_sessions: number;
  lab_present: number;
  lab_percentage: number;
  theory_sessions: number;
  theory_present: number;
  theory_percentage: number;
  below_threshold: boolean;
}

interface ReportResult {
  report_type: string;
  section_id: string;
  course_name: string;
  start_date: string;
  end_date: string;
  total_sessions: number;
  total_students: number;
  data: ReportData[];
}

export default function InstructorReports() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [instructorInfo, setInstructorInfo] = useState<any>(null);
  const [reportResult, setReportResult] = useState<ReportResult | null>(null);
  const [availableSections, setAvailableSections] = useState<string[]>([]);
  
  const [filters, setFilters] = useState({
    report_type: 'daily',
    section_id: '',
    course_name: '',
    start_date: '',
    end_date: '',
    specific_date: '2025-12-06' // Default to date with attendance data
  });

  useEffect(() => {
    loadInstructorInfo();
  }, []);

  useEffect(() => {
    if (filters.course_name) {
      loadSectionsForCourse(filters.course_name);
    } else {
      setAvailableSections([]);
      setFilters(prev => ({ ...prev, section_id: '' }));
    }
  }, [filters.course_name]);

  const loadInstructorInfo = async () => {
    try {
      const response = await instructorAPI.getInfo();
      setInstructorInfo(response.data);
      
      // Set default course if only one
      if (response.data.courses && response.data.courses.length === 1) {
        setFilters(prev => ({ ...prev, course_name: response.data.courses[0] }));
      }
    } catch (error) {
      toast.error('Failed to load instructor info');
      console.error(error);
    }
  };

  const loadSectionsForCourse = async (courseName: string) => {
    try {
      console.log('Loading sections for course:', courseName);
      // Get sections that have students enrolled in this course
      const response = await instructorAPI.getSectionsByCourse(courseName);
      const sections = response.data.sections || [];
      
      console.log('Received sections:', sections);
      setAvailableSections(sections);
      
      // Auto-select if only one section
      if (sections.length === 1) {
        setFilters(prev => ({ ...prev, section_id: sections[0] }));
      } else {
        // Reset section selection when course changes
        setFilters(prev => ({ ...prev, section_id: '' }));
      }
    } catch (error) {
      console.error('Failed to load sections:', error);
      toast.error('Failed to load sections for this course');
      setAvailableSections([]);
    }
  };

  const getDateRange = () => {
    const today = new Date();
    let start = '';
    let end = '';

    switch (filters.report_type) {
      case 'daily':
        start = filters.specific_date || today.toISOString().split('T')[0];
        end = start;
        break;
      
      case 'weekly':
        // Get start of current week (Monday)
        const startOfWeek = new Date(today);
        startOfWeek.setDate(today.getDate() - today.getDay() + 1);
        start = filters.start_date || startOfWeek.toISOString().split('T')[0];
        
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        end = filters.end_date || endOfWeek.toISOString().split('T')[0];
        break;
      
      case 'monthly':
        // Get start of current month
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        start = startOfMonth.toISOString().split('T')[0];
        
        const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        end = endOfMonth.toISOString().split('T')[0];
        break;
      
      case 'semester':
        // Assume semester is 4 months
        const startOfSemester = new Date(today);
        startOfSemester.setMonth(today.getMonth() - 4);
        start = startOfSemester.toISOString().split('T')[0];
        end = today.toISOString().split('T')[0];
        break;
      
      case 'yearly':
        // Get start of academic year (September)
        const currentYear = today.getMonth() >= 8 ? today.getFullYear() : today.getFullYear() - 1;
        start = `${currentYear}-09-01`;
        end = `${currentYear + 1}-08-31`;
        break;
      
      default:
        start = filters.start_date;
        end = filters.end_date;
    }

    return { start, end };
  };

  const handleGenerateReport = async () => {
    if (!filters.section_id) {
      toast.error('Please select a section');
      return;
    }

    if (!filters.course_name) {
      toast.error('Please select a course');
      return;
    }

    try {
      setLoading(true);
      
      const { start, end } = getDateRange();
      
      const reportFilters = {
        report_type: filters.report_type,
        section_id: filters.section_id,
        course_name: filters.course_name,
        start_date: start,
        end_date: end
      };
      
      const response = await instructorAPI.generateReport(reportFilters);
      setReportResult(response.data);
      toast.success('Report generated successfully!');
    } catch (error) {
      toast.error('Failed to generate report');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    if (!reportResult) {
      toast.error('Please generate a report first');
      return;
    }

    try {
      const { start, end } = getDateRange();
      
      const reportFilters = {
        report_type: filters.report_type,
        section_id: filters.section_id,
        course_name: filters.course_name,
        start_date: start,
        end_date: end
      };
      
      await instructorAPI.downloadReportCSV(reportFilters);
      toast.success('CSV downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download CSV');
      console.error(error);
    }
  };

  const handleDownloadExcel = async () => {
    if (!reportResult) {
      toast.error('Please generate a report first');
      return;
    }

    try {
      const { start, end } = getDateRange();
      
      const reportFilters = {
        report_type: filters.report_type,
        section_id: filters.section_id,
        course_name: filters.course_name,
        start_date: start,
        end_date: end
      };
      
      await instructorAPI.downloadReportExcel(reportFilters);
      toast.success('Excel downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download Excel');
      console.error(error);
    }
  };

  const belowThresholdCount = reportResult?.data.filter(s => s.below_threshold).length || 0;

  return (
    <Layout title="Attendance Reports">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/instructor')}
          className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to Dashboard</span>
        </button>
      </div>

      <div className="max-w-2xl mx-auto">
        {/* Report Configuration Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          {/* Icon and Title */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500 rounded-xl mb-3 shadow-lg">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-1">Download Reports</h1>
            <p className="text-sm text-gray-500">Generate attendance reports</p>
          </div>
          
          {/* Form Fields */}
          <div className="space-y-4">
            {/* Report Type */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Report Type</label>
              <select
                value={filters.report_type}
                onChange={(e) => setFilters({...filters, report_type: e.target.value})}
                className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
              >
                <option value="daily">Daily Report</option>
                <option value="weekly">Weekly Report</option>
                <option value="monthly">Monthly Report</option>
                <option value="semester">Semester Report</option>
                <option value="yearly">Yearly Report</option>
              </select>
            </div>

            {/* Course */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Course *</label>
              <select
                value={filters.course_name}
                onChange={(e) => setFilters({...filters, course_name: e.target.value})}
                className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
              >
                <option value="">Select Course</option>
                {instructorInfo?.courses?.map((course: string) => (
                  <option key={course} value={course}>
                    {course}
                  </option>
                ))}
              </select>
            </div>

            {/* Section */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Section *</label>
              <select
                value={filters.section_id}
                onChange={(e) => setFilters({...filters, section_id: e.target.value})}
                disabled={!filters.course_name}
                className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
              >
                <option value="">
                  {!filters.course_name ? 'Select Course First' : 'Select Section'}
                </option>
                {availableSections.map((section: string) => (
                  <option key={section} value={section}>
                    Section {section}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Inputs based on Report Type */}
            {filters.report_type === 'daily' && (
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Specific Date</label>
                <input
                  type="date"
                  value={filters.specific_date}
                  onChange={(e) => setFilters({...filters, specific_date: e.target.value})}
                  className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                />
              </div>
            )}

            {filters.report_type === 'weekly' && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Week Start</label>
                  <input
                    type="date"
                    value={filters.start_date}
                    onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                    className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Week End</label>
                  <input
                    type="date"
                    value={filters.end_date}
                    onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                    className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerateReport}
            disabled={loading || !filters.section_id || !filters.course_name}
            className="w-full mt-6 bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-bold text-base shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5" />
                <span>Generate Report</span>
              </>
            )}
          </button>
        </div>

        {/* Report Summary */}
        {reportResult && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow">
                <div className="text-sm opacity-90">Total Students</div>
                <div className="text-3xl font-bold mt-2">{reportResult.total_students}</div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow">
                <div className="text-sm opacity-90">Total Sessions</div>
                <div className="text-3xl font-bold mt-2">{reportResult.total_sessions}</div>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow">
                <div className="text-sm opacity-90">Section</div>
                <div className="text-3xl font-bold mt-2">{reportResult.section_id}</div>
              </div>
              
              <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-6 rounded-lg shadow">
                <div className="text-sm opacity-90">Below Threshold</div>
                <div className="text-3xl font-bold mt-2">{belowThresholdCount}</div>
              </div>
            </div>

            {/* Download Buttons */}
            <div className="flex space-x-2 mb-6">
              <button
                onClick={handleDownloadCSV}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="w-4 h-4" />
                <span>Download CSV</span>
              </button>
              <button
                onClick={handleDownloadExcel}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <FileSpreadsheet className="w-4 h-4" />
                <span>Download Excel</span>
              </button>
            </div>

            {/* Report Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Total Sessions</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Present</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Absent</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Overall %</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Lab %</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Theory %</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {reportResult.data.map((student) => (
                      <tr 
                        key={student.student_id} 
                        className={`hover:bg-gray-50 ${student.below_threshold ? 'bg-red-50' : ''}`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {student.student_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {student.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {student.section}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-900">
                          {student.total_sessions}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-green-600 font-medium">
                          {student.present_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-red-600 font-medium">
                          {student.absent_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            student.percentage >= 80 
                              ? 'bg-green-100 text-green-800' 
                              : student.percentage >= 60
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {student.percentage.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {student.lab_sessions > 0 ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              student.lab_percentage >= 100 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {student.lab_percentage.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {student.theory_sessions > 0 ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              student.theory_percentage >= 80 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {student.theory_percentage.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {student.below_threshold ? (
                            <span className="flex items-center justify-center space-x-1 text-red-600">
                              <AlertTriangle className="w-4 h-4" />
                              <span className="text-xs font-medium">Below</span>
                            </span>
                          ) : (
                            <span className="text-green-600 text-xs font-medium">OK</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-t">
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <div>
                    Showing {reportResult.data.length} students
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-100 border border-red-300 rounded"></div>
                      <span>Below Threshold</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Lab: 100% required | Theory: 80% required
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {!reportResult && !loading && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Report Generated</h3>
            <p className="text-gray-500">
              Configure your report settings above and click "Generate Report" to view attendance statistics
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
