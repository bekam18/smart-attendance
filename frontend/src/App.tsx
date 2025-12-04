import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { getStoredUser, isAuthenticated } from './lib/auth';

// Pages
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import AdminAllRecords from './pages/AdminAllRecords';
import AdminSettings from './pages/AdminSettings';
import AdminSessions from './pages/AdminSessions';
import AdminInstructors from './pages/AdminInstructors';
import AdminStudents from './pages/AdminStudents';
import InstructorDashboard from './pages/InstructorDashboard';
import StudentDashboard from './pages/StudentDashboard';
import AttendanceSession from './pages/AttendanceSession';
import AttendanceRecords from './pages/AttendanceRecords';
import InstructorSettings from './pages/InstructorSettings';
import InstructorReports from './pages/InstructorReports';

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles: string[] }) {
  const user = getStoredUser();
  
  if (!isAuthenticated() || !user) {
    return <Navigate to="/login" replace />;
  }
  
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  const user = getStoredUser();
  
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/"
          element={
            isAuthenticated() && user ? (
              user.role === 'admin' ? (
                <Navigate to="/admin" replace />
              ) : user.role === 'instructor' ? (
                <Navigate to="/instructor" replace />
              ) : (
                <Navigate to="/student" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/records"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminAllRecords />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/settings"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminSettings />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/sessions"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminSessions />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/instructors"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminInstructors />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/students"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminStudents />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/instructor"
          element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <InstructorDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/instructor/session/:sessionId"
          element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <AttendanceSession />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/instructor/records"
          element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <AttendanceRecords />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/instructor/settings"
          element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <InstructorSettings />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/instructor/reports"
          element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <InstructorReports />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/student"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
