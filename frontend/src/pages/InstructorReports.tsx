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
  message?: string;
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
    specific_date: new Date().toISOString().split('T')[0], // Today's date
    week_start: new Date().toISOString().split('T')[0], // Week start date
    week_end: (() => {
      const startDate = new Date();
      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 6);
      return endDate.toISOString().split('T')[0];
    })(), // Week end date (automatically calculated)
    selected_month: new Date().getMonth() + 1, // Current month (1-12)
    selected_year: new Date().getFullYear() // Current year
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
        start = filters.specific_date;
        end = start;
        break;
      
      case 'weekly':
        // Use week start date entered by instructor, add 7 days for end
        const weekStartDate = new Date(filters.week_start);
        start = filters.week_start;
        
        const weekEndDate = new Date(weekStartDate);
        weekEndDate.setDate(weekStartDate.getDate() + 6); // Add 6 days (7 days total)
        end = weekEndDate.toISOString().split('T')[0];
        break;
      
      case 'monthly':
        // Use selected month and year
        const startOfMonth = new Date(filters.selected_year, filters.selected_month - 1, 1);
        start = startOfMonth.toISOString().split('T')[0];
        
        const endOfMonth = new Date(filters.selected_year, filters.selected_month, 0);
        end = endOfMonth.toISOString().split('T')[0];
        break;
      
      case 'semester':
        // Semester is typically 4-5 months, use current semester logic
        const currentMonth = today.getMonth();
        if (currentMonth >= 8) {
          // Fall semester (September - January)
          start = `${today.getFullYear()}-09-01`;
          end = `${today.getFullYear() + 1}-01-31`;
        } else if (currentMonth >= 1 && currentMonth <= 4) {
          // Spring semester (February - May)
          start = `${today.getFullYear()}-02-01`;
          end = `${today.getFullYear()}-05-31`;
        } else {
          // Summer semester (June - August)
          start = `${today.getFullYear()}-06-01`;
          end = `${today.getFullYear()}-08-31`;
        }
        break;
      
      case 'yearly':
        // Use selected year (academic year: September to August)
        start = `${filters.selected_year}-09-01`;
        end = `${filters.selected_year + 1}-08-31`;
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
      
      // Check if there's no data for the selected period
      if (response.data.total_sessions === 0 || response.data.data.length === 0) {
        toast.error(response.data.message || `No attendance data found for the selected ${filters.report_type} period`);
      } else {
        toast.success('Report generated successfully!');
      }
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

    if (reportResult.total_sessions === 0) {
      toast.error('No data available to download');
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

    if (reportResult.total_sessions === 0) {
      toast.error('No data available to download');
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

  // Helper function to get available years (last 5 years + current + next 2)
  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear - 5; i <= currentYear + 2; i++) {
      years.push(i);
    }
    return years;
  };

  // Helper function to get month names
  const getMonthNames = () => [
    { value: 1, name: 'January' },
    { value: 2, name: 'February' },
    { value: 3, name: 'March' },
    { value: 4, name: 'April' },
    { value: 5, name: 'May' },
    { value: 6, name: 'June' },
    { value: 7, name: 'July' },
    { value: 8, name: 'August' },
    { value: 9, name: 'September' },
    { value: 10, name: 'October' },
    { value: 11, name: 'November' },
    { value: 12, name: 'December' }
  ];

  // Helper function to calculate week end date when week start changes
  const handleWeekStartChange = (weekStart: string) => {
    const startDate = new Date(weekStart);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 6);
    
    setFilters({
      ...filters, 
      week_start: weekStart,
      week_end: endDate.toISOString().split('T')[0] // Update week end date
    });
  };

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
                <option value="daily">📅 Daily Report</option>
                <option value="weekly">📊 Weekly Report</option>
                <option value="monthly">📈 Monthly Report</option>
                <option value="semester">🎓 Semester Report</option>
                <option value="yearly">📋 Yearly Report</option>
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
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Select Date</label>
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
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Week Start Date</label>
                  <input
                    type="date"
                    value={filters.week_start}
                    onChange={(e) => handleWeekStartChange(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Week End Date</label>
                  <input
                    type="date"
                    value={filters.week_end}
                    readOnly
                    disabled
                    className="w-full px-4 py-2.5 bg-gray-100 border-2 border-gray-200 rounded-lg text-sm text-gray-600 cursor-not-allowed"
                  />
                </div>
                {filters.week_start && (
                  <div className="col-span-2 mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <strong>Week Period:</strong> {filters.week_start} to {(() => {
                        const endDate = new Date(filters.week_start);
                        endDate.setDate(endDate.getDate() + 6);
                        return endDate.toISOString().split('T')[0];
                      })()}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      System automatically calculates 7-day period from start date
                    </p>
                  </div>
                )}
              </div>
            )}

            {filters.report_type === 'monthly' && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Month</label>
                  <select
                    value={filters.selected_month}
                    onChange={(e) => setFilters({...filters, selected_month: parseInt(e.target.value)})}
                    className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  >
                    {getMonthNames().map((month) => (
                      <option key={month.value} value={month.value}>
                        {month.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">Year</label>
                  <select
                    value={filters.selected_year}
                    onChange={(e) => setFilters({...filters, selected_year: parseInt(e.target.value)})}
                    className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  >
                    {getAvailableYears().map((year) => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {filters.report_type === 'semester' && (
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Current Semester</label>
                <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg">
                  <div className="text-sm text-purple-800 font-medium mb-2">
                    🎓 Automatic Semester Detection
                  </div>
                  <div className="text-sm text-purple-700">
                    {(() => {
                      const today = new Date();
                      const currentMonth = today.getMonth();
                      let semesterInfo = '';
                      
                      if (currentMonth >= 8) {
                        // Fall semester (September - January)
                        semesterInfo = `Fall Semester: September ${today.getFullYear()} - January ${today.getFullYear() + 1}`;
                      } else if (currentMonth >= 1 && currentMonth <= 4) {
                        // Spring semester (February - May)
                        semesterInfo = `Spring Semester: February ${today.getFullYear()} - May ${today.getFullYear()}`;
                      } else {
                        // Summer semester (June - August)
                        semesterInfo = `Summer Semester: June ${today.getFullYear()} - August ${today.getFullYear()}`;
                      }
                      
                      return semesterInfo;
                    })()}
                  </div>
                  <div className="text-xs text-purple-600 mt-2">
                    System automatically detects current semester based on today's date
                  </div>
                </div>
              </div>
            )}

            {filters.report_type === 'yearly' && (
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">Academic Year</label>
                <select
                  value={filters.selected_year}
                  onChange={(e) => setFilters({...filters, selected_year: parseInt(e.target.value)})}
                  className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                >
                  {getAvailableYears().map((year) => (
                    <option key={year} value={year}>
                      {year}-{year + 1} Academic Year
                    </option>
                  ))}
                </select>
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Academic Year Period:</strong> September {filters.selected_year} to August {filters.selected_year + 1}
                  </p>
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
            {reportResult.total_sessions === 0 ? (
              /* No Data Found */
              <div className="bg-white rounded-2xl shadow-lg p-8 mb-6 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-500 rounded-xl mb-4 shadow-lg">
                  <AlertTriangle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">No Data Found</h3>
                <p className="text-gray-600 mb-4">
                  {reportResult.message || `No attendance sessions found for the selected ${reportResult.report_type} period.`}
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Selected Period:</strong> {reportResult.start_date} to {reportResult.end_date}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    Try selecting a different time period with existing attendance sessions.
                  </p>
                </div>
              </div>
            ) : (
              /* Report Data Found */
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
            )}

            {/* Download Buttons - Only show when there's data */}
            {reportResult.total_sessions > 0 && (
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
            )}

            {/* Report Table - Only show when there's data */}
            {reportResult.total_sessions > 0 && (
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
            )}
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
