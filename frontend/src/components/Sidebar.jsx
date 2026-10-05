import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  DoorClosed,
  AlertCircle,
  ClipboardCheck,
  Compass,
  FilePlus,
  PlusCircle,
  LogOut,
  X,
  Building2,
  User,
  Shield,
  Layers,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = ({ mobileOpen, setMobileOpen }) => {
  const location = useLocation();
  const { user, logout, isWardenOrAdmin } = useAuth();

  const isActive = (path) => {
    if (path === '/' && (location.pathname === '/' || location.pathname === '/overview')) {
      return true;
    }
    return location.pathname === path;
  };

  const mainNav = isWardenOrAdmin
    ? [
        {
          name: 'Overview',
          path: '/',
          icon: LayoutDashboard,
          badge: null,
        },
        {
          name: 'Room allocation',
          path: '/rooms',
          icon: DoorClosed,
          badge: null,
        },
        {
          name: 'Complaints',
          path: '/complaints',
          icon: AlertCircle,
          badge: '10',
          badgeColor: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
        },
        {
          name: 'Attendance',
          path: '/attendance',
          icon: ClipboardCheck,
          badge: null,
        },
        {
          name: 'Leave tracking',
          path: '/leaves',
          icon: Compass,
          badge: null,
        },
      ]
    : [
        {
          name: 'Overview',
          path: '/',
          icon: LayoutDashboard,
          badge: null,
        },
        {
          name: 'My complaints',
          path: '/complaints',
          icon: AlertCircle,
          badge: null,
        },
        {
          name: 'My gate passes',
          path: '/leaves',
          icon: Compass,
          badge: null,
        },
      ];

  const quickActions = isWardenOrAdmin
    ? [
        {
          name: 'Register complaint',
          path: '/register-complaint',
          icon: PlusCircle,
        },
      ]
    : [
        {
          name: 'Apply leave',
          path: '/apply-leave',
          icon: FilePlus,
        },
        {
          name: 'Register complaint',
          path: '/register-complaint',
          icon: PlusCircle,
        },
      ];

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#111827] text-slate-300 flex flex-col justify-between border-r border-slate-800 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex-1 flex flex-col min-h-0">
          {/* Brand Header */}
          <div className="p-4 flex items-center justify-between border-b border-slate-800">
            <Link to="/" className="flex items-center gap-3 group" onClick={() => setMobileOpen(false)}>
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white font-extrabold flex items-center justify-center text-sm shadow-md shadow-teal-900/30 group-hover:scale-105 transition-transform">
                HM
              </div>
              <div>
                <h1 className="text-white font-bold text-base tracking-tight leading-none group-hover:text-teal-400 transition-colors">
                  HostelOS
                </h1>
                <p className="text-[11px] text-slate-400 mt-1 font-medium leading-none">
                  Hostel Operations System
                </p>
              </div>
            </Link>

            <button
              onClick={() => setMobileOpen(false)}
              className="lg:hidden p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
            <div>
              <p className="px-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Operations
              </p>
              <nav className="space-y-1">
                {mainNav.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);

                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                        active
                          ? 'bg-teal-600/15 text-teal-400 font-semibold border-l-4 border-teal-500 rounded-l-none'
                          : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`w-4 h-4 ${active ? 'text-teal-400' : 'text-slate-400'}`} />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${item.badgeColor}`}>
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>

            <div>
              <p className="px-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                {isWardenOrAdmin ? 'Quick Actions' : 'Resident Actions'}
              </p>
              <nav className="space-y-1">
                {quickActions.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);

                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                        active
                          ? 'bg-teal-600/15 text-teal-400 font-semibold border-l-4 border-teal-500 rounded-l-none'
                          : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${active ? 'text-teal-400' : 'text-slate-400'}`} />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/60 space-y-3">
          {/* Project Details */}
          <div className="px-2 py-1.5 rounded bg-slate-950/40 border border-slate-800/60 text-[11px] text-slate-400">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-300">HostelOS v2.4</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">Group C9 · 23CSE202 (DBMS)</div>
          </div>

          {/* User Profile Card */}
          {user ? (
            <div className="p-2 rounded-xl bg-slate-800/60 border border-slate-700/50 flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-xs shrink-0 border border-teal-500/30">
                  {user.name.charAt(0)}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-white truncate leading-tight">
                    {user.name}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate mt-0.5">
                    {user.role} {user.room_number ? `· ${user.room_number}` : ''}
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign out"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-700/50 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors"
            >
              <User className="w-4 h-4" />
              Sign in
            </Link>
          )}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
