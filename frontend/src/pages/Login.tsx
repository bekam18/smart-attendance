import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LogIn, Scan, Phone, Mail, Globe, Sparkles } from 'lucide-react';
import { authAPI } from '../lib/api';
import { setAuth } from '../lib/auth';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedUsername = username.trim();
    const trimmedPassword = password.trim();
    
    if (!trimmedUsername || !trimmedPassword) {
      toast.error('Please enter username and password');
      return;
    }

    setLoading(true);
    
    try {
      const response = await authAPI.login(trimmedUsername, trimmedPassword);
      const { access_token, user } = response.data;
      
      setAuth(access_token, user);
      toast.success(`Welcome, ${user.name}!`);
      
      if (user.role === 'admin') {
        navigate('/admin');
      } else if (user.role === 'instructor') {
        navigate('/instructor');
      } else {
        navigate('/student');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col">
      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 pt-24">
        <div className="w-full max-w-md">
          {/* Login Card */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {/* Logo & Title */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500 rounded-xl mb-3 shadow-lg">
                <Scan className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-800 mb-1">
                SmartAttendance Using Face Recognition
              </h1>
              <p className="text-sm text-gray-500">Secure Access Portal</p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  placeholder="Enter your username"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-50 border-2 border-gray-200 rounded-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all duration-300 outline-none hover:border-blue-300 text-sm"
                  placeholder="Enter your password"
                  disabled={loading}
                />
              </div>

              <div className="text-right">
                <button
                  type="button"
                  onClick={() => navigate('/forgot-password')}
                  className="text-xs text-blue-500 hover:text-blue-600 font-medium"
                >
                  Forgot password?
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-bold text-base shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Logging in...</span>
                  </>
                ) : (
                  <>
                    <LogIn className="w-5 h-5" />
                    <span>Login</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Motto */}
          <div className="text-center mt-6">
            <p className="text-blue-600 text-sm font-semibold flex items-center justify-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span>SmartAttendance — Where AI Meets Accuracy</span>
              <Sparkles className="w-4 h-4" />
            </p>
          </div>
        </div>
      </div>

      {/* Footer Contact Cards */}
      <footer className="bg-white border-t py-8 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            {/* Phone */}
            <div className="bg-white border-2 border-gray-100 rounded-xl p-4 text-center hover:shadow-lg transition-shadow">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-500 rounded-lg mb-3">
                <Phone className="w-6 h-6 text-white" />
              </div>
              <p className="font-semibold text-gray-800 text-sm mb-1">Phone</p>
              <p className="text-xs text-gray-600">+251 918079603</p>
              <p className="text-xs text-gray-600">+251 974791353</p>
            </div>

            {/* Email */}
            <div className="bg-white border-2 border-gray-100 rounded-xl p-4 text-center hover:shadow-lg transition-shadow">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-500 rounded-lg mb-3">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <p className="font-semibold text-gray-800 text-sm mb-1">Email</p>
              <p className="text-xs text-gray-600">info@smartattendance.com</p>
            </div>

            {/* Website */}
            <div className="bg-white border-2 border-gray-100 rounded-xl p-4 text-center hover:shadow-lg transition-shadow">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-500 rounded-lg mb-3">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <p className="font-semibold text-gray-800 text-sm mb-1">Website</p>
              <p className="text-xs text-gray-600">smartattendance.com</p>
            </div>
          </div>

          {/* Copyright */}
          <div className="text-center pt-4 border-t">
            <p className="text-gray-500 text-xs">
              © 2025 SmartAttendance. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
