import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, Eye, EyeOff, AlertCircle, LogIn, Shield, Users, GraduationCap } from 'lucide-react';
import { formatErrorMessage } from '../utils/errorHandler';

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      console.error(err);
      setError(
        formatErrorMessage(err, 'Invalid email or password. Please verify credentials.')
      );
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError('');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-teal-600 text-white font-extrabold text-base flex items-center justify-center mx-auto shadow-md shadow-teal-900/30 mb-3">
            HM
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            HostelOS Sign In
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Group C9 · 23CSE202 (Database Management Systems)
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-7 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 flex items-start gap-2.5 text-rose-700 dark:text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-500" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">
                Campus Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@hostelos.in"
                  className="w-full pl-10 pr-4 py-2.5 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-teal-600 hover:bg-teal-500 disabled:opacity-50 text-white font-semibold rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all text-xs"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Autofill */}
          <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-700">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 text-center">
              1-Click Demo Profiles (DBMS Evaluation)
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => fillCredentials('admin@hostelos.in', 'Admin@123')}
                className="py-1.5 px-2 text-[10px] font-bold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 rounded-lg border border-purple-200 dark:border-purple-800 transition-colors text-center"
              >
                College Head
              </button>
              <button
                type="button"
                onClick={() => fillCredentials('warden@hostelos.in', 'Warden@123')}
                className="py-1.5 px-2 text-[10px] font-bold text-teal-700 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 hover:bg-teal-100 rounded-lg border border-teal-200 dark:border-teal-800 transition-colors text-center"
              >
                Chief Warden
              </button>
              <button
                type="button"
                onClick={() => fillCredentials('siddharth@hostelos.in', 'Student@123')}
                className="py-1.5 px-2 text-[10px] font-bold text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/40 hover:bg-blue-100 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors text-center"
              >
                Student
              </button>
            </div>
          </div>

          {/* Link to Register */}
          <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-5">
            New resident student?{' '}
            <Link to="/register" className="font-semibold text-teal-600 dark:text-teal-400 hover:underline">
              Register account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
