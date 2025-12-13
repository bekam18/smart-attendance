import axios from 'axios';

// @ts-ignore - Vite env variables
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  config.headers = config.headers || {};
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // If we're sending FormData, don't force Content-Type: let the browser/axios set the boundary
  // Otherwise, default to application/json for normal requests.
  try {
    if (config.data instanceof FormData) {
      if (config.headers['Content-Type']) delete config.headers['Content-Type'];
    } else {
      config.headers['Content-Type'] = 'application/json';
    }
  } catch (e) {
    // If FormData or headers access fails for any reason, fall back to leaving headers alone.
  }

  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/api/auth/login', { username, password }),
  
  registerStudent: (data: any) =>
    api.post('/api/auth/register-student', data),
  
  getCurrentUser: () =>
    api.get('/api/auth/me'),
  
  forgotPassword: (email: string) =>
    api.post('/api/auth/forgot-password', { email }),
  
  verifyResetToken: (token: string) =>
    api.post('/api/auth/verify-reset-token', { token }),
  
  resetPassword: (token: string, password: string) =>
    api.post('/api/auth/reset-password', { token, password }),
};

// Admin API
export const adminAPI = {
  addInstructor: (data: any) =>
    api.post('/api/admin/add-instructor', data),
  
  addStudent: (data: any) =>
    api.post('/api/admin/add-student', data),
  

  
  getStudents: () =>
    api.get('/api/admin/students'),
  
  deleteInstructor: (instructorId: string) =>
    api.delete(`/api/admin/instructor/${instructorId}`),
  
  deleteStudent: (studentId: string) =>
    api.delete(`/api/admin/student/${studentId}`),
  
  getAllAttendance: (params?: any) =>
    api.get('/api/admin/attendance/all', { params }),
  
  uploadModel: (file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    // Let axios set Content-Type (including boundary)
    return api.post('/api/admin/upload-model', formData);
  },
  
  getStats: (date?: string) =>
    api.get('/api/admin/stats', { params: date ? { date } : {} }),
  
  exportAttendanceCSV: async (filters?: any) => {
    const response = await api.get('/api/admin/attendance/export/csv', {
      params: filters,
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `all_attendance_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  exportAttendanceExcel: async (filters?: any) => {
    const response = await api.get('/api/admin/attendance/export/excel', {
      params: filters,
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `all_attendance_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  getAdminSettings: () =>
    api.get('/api/admin/settings'),
  
  updateAdminSettings: (settings: any) =>
    api.put('/api/admin/settings', settings),
  
  getInstructors: () =>
    api.get('/api/admin/get-instructors'),
  
  updateInstructorSections: (instructorId: number, sections: string[]) =>
    api.post('/api/admin/update-instructor-sections', {
      instructor_id: instructorId,
      sections: sections
    }),
  
  getActiveSessions: (filters?: any) =>
    api.get('/api/admin/active-sessions', { params: filters }),
  
  getRecentSessions: (filters?: any) =>
    api.get('/api/admin/recent-sessions', { params: filters }),
  
  toggleInstructor: (instructorId: string) =>
    api.put(`/api/admin/instructor/${instructorId}/toggle`),
  
  toggleStudent: (studentId: string) =>
    api.put(`/api/admin/student/${studentId}/toggle`),
  
  updateInstructor: (instructorId: string, data: any) =>
    api.put(`/api/admin/instructor/${instructorId}`, data),
  
  updateStudent: (studentId: string, data: any) =>
    api.put(`/api/admin/student/${studentId}`, data),
  
  // Session Management
  getAllSessions: () =>
    api.get('/api/attendance/sessions'),
  
  adminReopenSession: (sessionId: number) =>
    api.post('/api/attendance/admin-reopen-session', { session_id: sessionId }),
  
  // Analytics API
  getSectionAttendanceAnalytics: () =>
    api.get('/api/admin/analytics/section-attendance'),
  
  getDailyAttendanceAnalytics: () =>
    api.get('/api/admin/analytics/daily-attendance'),
  
  getCoursePerformanceAnalytics: () =>
    api.get('/api/admin/analytics/course-performance'),
  
  getInstructorPerformanceAnalytics: () =>
    api.get('/api/admin/analytics/instructor-performance'),
  
  getTimeBlockAnalysis: () =>
    api.get('/api/admin/analytics/time-block-analysis'),
  
  getMonthlyAttendanceAnalytics: () =>
    api.get('/api/admin/analytics/monthly-attendance'),
  
  getInstructorActivityAnalytics: () =>
    api.get('/api/admin/analytics/instructor-activity'),
  
  getSessionTypeComparison: () =>
    api.get('/api/admin/analytics/session-type-comparison'),
  
  getRecentInstructorSessions: () =>
    api.get('/api/admin/analytics/recent-instructor-sessions'),
};

// Student API
export const studentAPI = {
  getProfile: () =>
    api.get('/api/students/profile'),
  
  registerFace: (images: File[]) => {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append('images', image);
    });
    return api.post('/api/students/register-face', formData);
  },
  
  getAttendance: () =>
    api.get('/api/students/attendance'),
};

// Attendance API
export const attendanceAPI = {
  startSession: (data: any) =>
    api.post('/api/attendance/start-session', data),
  
  endSession: (sessionId: string, endType: 'daily' | 'semester' = 'semester') =>
    api.post('/api/attendance/end-session', { session_id: sessionId, end_type: endType }),
  
  markAbsent: (sessionId: string) =>
    api.post('/api/attendance/mark-absent', { session_id: sessionId }),
  

  
  checkSemesterEligibility: (data: { course_name: string; section_id: string; year: string }) =>
    api.post('/api/attendance/check-semester-eligibility', data),
  
  recognize: async (image: Blob | string, sessionId: string) => {
    console.log('🔍 Sending recognition request...');
    console.log('Session ID:', sessionId);
    console.log('Image type:', typeof image);

    try {
      // Convert image to File object for proper multipart/form-data upload
      let file: File;

      if (typeof image === 'string') {
        // Convert base64/data URL to Blob then File
        let dataUrl = image;
        if (!image.startsWith('data:')) {
          dataUrl = 'data:image/jpeg;base64,' + image;
        }
        const res = await fetch(dataUrl);
        const blob = await res.blob();
        file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      } else {
        // Convert Blob to File
        const blob = image as Blob;
        file = blob instanceof File 
          ? blob 
          : new File([blob], 'capture.jpg', { type: blob.type || 'image/jpeg' });
      }

      console.log('File created:', file.name, file.type, file.size, 'bytes');

      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('image', file);

      console.log('Sending FormData to /api/attendance/recognize');
      console.log('FormData entries:', Array.from(formData.entries()).map(([k, v]) => 
        `${k}: ${v instanceof File ? `File(${v.name}, ${v.size}b)` : v}`
      ));

      // Send request. Let the request interceptor attach Authorization and the
      // browser/axios set the multipart Content-Type (with boundary).
      const response = await api.post('/api/attendance/recognize', formData);

      console.log('✅ Response:', response.data);
      return response;

    } catch (error: any) {
      console.error('❌ Recognition error:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
      });
      throw error;
    }
  },
  
  getSessionAttendance: (sessionId: string) =>
    api.get(`/api/attendance/session/${sessionId}`),
  
  getStudentAttendance: (studentId: string) =>
    api.get(`/api/attendance/student/${studentId}`),
  
  getSessions: () =>
    api.get('/api/attendance/sessions'),
  
  instructorReopenSession: (sessionId: number) =>
    api.post('/api/attendance/instructor-reopen-session', { session_id: sessionId }),
};

// Instructor API
export const instructorAPI = {
  getInfo: () =>
    api.get('/api/instructor/info'),
  
  getRecords: (filters?: any) =>
    api.get('/api/instructor/records', { params: filters }),
  
  exportCSV: async (filters?: any) => {
    const response = await api.get('/api/instructor/records/export/csv', {
      params: filters,
      responseType: 'blob'
    });
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `attendance_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  exportExcel: async (filters?: any) => {
    const response = await api.get('/api/instructor/records/export/excel', {
      params: filters,
      responseType: 'blob'
    });
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `attendance_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  getSettings: () =>
    api.get('/api/instructor/settings'),
  
  updateSettings: (settings: any) =>
    api.put('/api/instructor/settings', settings),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.put('/api/instructor/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    }),
  
  getStudentsList: () =>
    api.get('/api/instructor/students'),
  
  getSectionsByCourse: (courseName: string) =>
    api.get('/api/instructor/sections-by-course', { params: { course_name: courseName } }),
  
  generateReport: (filters: any) =>
    api.post('/api/instructor/reports/generate', filters),
  
  downloadReportCSV: async (filters: any) => {
    const response = await api.post('/api/instructor/reports/download/csv', filters, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const reportType = filters.report_type || 'custom';
    link.setAttribute('download', `attendance_report_${reportType}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  downloadReportExcel: async (filters: any) => {
    const response = await api.post('/api/instructor/reports/download/excel', filters, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const reportType = filters.report_type || 'custom';
    link.setAttribute('download', `attendance_report_${reportType}_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

// Debug API
export const debugAPI = {
  echo: () =>
    api.get('/api/debug/echo'),
  
  testRecognition: (image: Blob) => {
    const formData = new FormData();
    formData.append('image', image);
    return api.post('/api/debug/recognition-test', formData);
  },
  
  getModelStatus: () =>
    api.get('/api/debug/model-status'),
};
