import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import {
  Menu,
  LogOut,
  ChevronRight,
  ChevronDown,
  LogIn,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const TopHeader = ({ onMenuClick }) => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const getPageInfo = () => {
    const path = location.pathname;
    if (path === '/' || path === '/overview') {
      return { title: 'Operations overview', crumbs: ['HostelOS', 'Administration', 'Overview'] };
    }
    if (path === '/rooms') {
      return { title: 'Room allocation', crumbs: ['HostelOS', 'Hostel Admin', 'Room Allocation'] };
    }
    if (path === '/complaints') {
      return { title: 'Complaint management', crumbs: ['HostelOS', 'Operations', 'Complaints'] };
    }
    if (path === '/attendance') {
      return { title: 'Daily attendance register', crumbs: ['HostelOS', 'Hostel Admin', 'Attendance'] };
    }
    if (path === '/leaves') {
      return { title: 'Leave tracking', crumbs: ['HostelOS', 'Hostel Admin', 'Gate Passes'] };
    }
    if (path === '/apply-leave') {
      return { title: 'Apply for leave / gate pass', crumbs: ['HostelOS', 'Resident', 'Apply Leave'] };
    }
    if (path === '/register-complaint') {
      return { title: 'Register complaint', crumbs: ['HostelOS', 'Resident', 'New Complaint'] };
    }
    return { title: 'HostelOS Portal', crumbs: ['HostelOS', 'Portal'] };
  };

  const { title, crumbs } = getPageInfo();

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left side: Hamburger & Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div>
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-0.5">
              {crumbs.map((crumb, idx) => (
                <React.Fragment key={crumb}>
                  {idx > 0 && <ChevronRight className="w-3 h-3 text-slate-400" />}
                  <span className={idx === crumbs.length - 1 ? 'font-semibold text-slate-700 dark:text-slate-200' : ''}>
                    {crumb}
                  </span>
                </React.Fragment>
              ))}
            </div>
            <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight">
              {title}
            </h1>
          </div>
        </div>

        {/* Center / Right Controls */}
        <div className="flex items-center gap-3 sm:gap-4">


          {/* User Profile */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-teal-600 text-white font-bold text-xs flex items-center justify-center shadow-sm">
                  {user.name.charAt(0)}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-tight">
                    {user.name}
                  </p>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    {user.role}
                  </p>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {profileDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setProfileDropdownOpen(false)} />
                  <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white dark:bg-slate-900 shadow-xl border border-slate-200 dark:border-slate-800 z-50 p-2 space-y-1">
                    <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800">
                      <p className="text-xs font-bold text-slate-800 dark:text-white truncate">{user.name}</p>
                      <p className="text-[11px] text-slate-500 truncate">{user.email}</p>
                      {user.roll_number && (
                        <p className="text-[10px] text-teal-600 dark:text-teal-400 mt-1 font-mono">
                          {user.roll_number}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={logout}
                      className="w-full text-left px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg flex items-center gap-2"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      Sign out
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign in</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
