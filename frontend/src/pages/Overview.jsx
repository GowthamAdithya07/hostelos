import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  AlertTriangle,
  FileCheck2,
  CalendarCheck2,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  ChevronRight,
  RefreshCw,
  Building,
  ShieldAlert,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export const Overview = () => {
  const { user, isWardenOrAdmin } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchOverviewData = async () => {
    try {
      setRefreshing(true);
      const res = await api.get('/analytics/overview');
      setMetrics(res.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const getUrgencyBadge = (urgency) => {
    switch (urgency) {
      case 'High':
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30';
      case 'Medium':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30';
      default:
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/30';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Resolved':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30';
      case 'Escalated':
        return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/30';
      default:
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Aggregating hostel metrics...</p>
        </div>
      </div>
    );
  }

  const {
    total_beds = 54,
    filled_beds = 42,
    occupancy_pct = 78,
    active_complaints = 10,
    needs_triage_count = 4,
    pending_leaves = 4,
    attendance_today_pct = 90,
    recent_complaints = [],
    approved_passes = [],
  } = metrics || {};

  return (
    <div className="space-y-6">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            {isWardenOrAdmin ? 'Hostel Operations Overview' : 'Resident Portal Overview'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            {isWardenOrAdmin
              ? 'Real-time occupancy, open complaints, gate passes, and daily night roll-call'
              : `Welcome back, ${user?.name || 'Resident'}. View your room status, tickets, and gate passes.`}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchOverviewData}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-teal-600' : ''}`} />
            <span>Refresh</span>
          </button>

          <Link
            to="/register-complaint"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <span>+ Register complaint</span>
          </Link>
        </div>
      </div>

      {/* 4 KPI CARDS (Matches C9 Hostelos_image1.png) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        {/* KPI 1 */}
        {isWardenOrAdmin ? (
          <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-teal-500/50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Total Occupancy
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                    {filled_beds}/{total_beds}
                  </span>
                  <span className="text-xs font-bold text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/50 px-2 py-0.5 rounded-full border border-teal-200 dark:border-teal-800/60">
                    {occupancy_pct}%
                  </span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-4">
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-teal-500 h-2 rounded-full transition-all duration-700"
                  style={{ width: `${occupancy_pct}%` }}
                ></div>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                {occupancy_pct}% filled across 3 blocks (A, B, C)
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-teal-500/50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Allocated Room
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                    {user?.room_number || 'A-101'}
                  </span>
                  <span className="text-xs font-bold text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/50 px-2 py-0.5 rounded-full border border-teal-200 dark:border-teal-800/60">
                    Block {user?.block || 'A'}
                  </span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
                <Building className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Bed Allocated & Active
              </span>
              <span className="text-slate-400 font-mono text-[10px]">{user?.roll_number}</span>
            </div>
          </div>
        )}

        {/* KPI 2: Active Complaints */}
        <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-amber-500/50 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {isWardenOrAdmin ? 'Active Complaints' : 'My Open Issues'}
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                  {active_complaints}
                </span>
                <span className="text-xs font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/50 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-800/60">
                  {active_complaints > 0 ? `${active_complaints} active` : 'All clear'}
                </span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 dark:text-slate-400">
              {isWardenOrAdmin ? (
                <>
                  <strong className="text-rose-500 font-semibold">{needs_triage_count} High urgency</strong> · Needs triage
                </>
              ) : (
                'Under technician resolution'
              )}
            </span>
            <Link to="/complaints" className="text-teal-600 dark:text-teal-400 font-semibold hover:underline">
              {isWardenOrAdmin ? 'View →' : 'My tickets →'}
            </Link>
          </div>
        </div>

        {/* KPI 3: Pending Leaves */}
        <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-blue-500/50 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {isWardenOrAdmin ? 'Pending Leaves' : 'My Gate Passes'}
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                  {pending_leaves}
                </span>
                <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50 px-2 py-0.5 rounded-full border border-blue-200 dark:border-blue-800/60">
                  {isWardenOrAdmin ? 'Gate Passes' : 'Pending'}
                </span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <FileCheck2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
            <span className="text-slate-500 dark:text-slate-400">
              {isWardenOrAdmin ? 'Awaiting warden approval · 2 leaving today' : 'Out-station permits & passes'}
            </span>
            <Link to="/leaves" className="text-teal-600 dark:text-teal-400 font-semibold hover:underline">
              {isWardenOrAdmin ? 'Review →' : 'My passes →'}
            </Link>
          </div>
        </div>

        {/* KPI 4: Attendance Today */}
        {isWardenOrAdmin ? (
          <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Attendance Today
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                    {attendance_today_pct}%
                  </span>
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/60">
                    Roll-call
                  </span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <CalendarCheck2 className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
              <span className="text-slate-500 dark:text-slate-400">Night roll-call · 4 flagged / absent</span>
              <Link to="/attendance" className="text-teal-600 dark:text-teal-400 font-semibold hover:underline">
                Roster &rarr;
              </Link>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-sm relative overflow-hidden group hover:border-emerald-500/50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Night Roll-Call
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                    Good Standing
                  </span>
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/60">
                    Regular
                  </span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <CalendarCheck2 className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-[11px]">
              <span className="text-slate-500 dark:text-slate-400">Night biometric attendance verified</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active</span>
            </div>
          </div>
        )}
      </div>

      {/* SPLIT SECTION (Matches C9 Hostelos_image1.png) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2/3 width): Recent Complaints */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden">
          <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                {isWardenOrAdmin ? 'Recent Complaints' : 'My Recent Complaints'}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {isWardenOrAdmin
                  ? 'Latest maintenance and facility issues submitted by residents'
                  : 'Latest maintenance and facility issues submitted by you'}
              </p>
            </div>
            <Link
              to="/complaints"
              className="text-xs font-semibold text-teal-600 dark:text-teal-400 hover:text-teal-700 flex items-center gap-1"
            >
              <span>{isWardenOrAdmin ? `View all (${active_complaints})` : 'View my tickets'}</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-700/60">
            {recent_complaints.length > 0 ? (
              recent_complaints.slice(0, 5).map((complaint) => (
                <div
                  key={complaint.id}
                  className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors flex items-center justify-between gap-4"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">
                        {complaint.ticket_number}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium">
                        {complaint.category}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${getUrgencyBadge(complaint.urgency)}`}>
                        {complaint.urgency}
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white mt-1 truncate">
                      {complaint.title}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {isWardenOrAdmin
                        ? `${complaint.student?.name || 'Resident'} · Room ${complaint.student?.room_number || 'A-Wing'}`
                        : `Filed: ${new Date(complaint.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}`}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${getStatusBadge(complaint.status)}`}>
                      {complaint.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs text-slate-400 font-medium">
                No active complaints registered.
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1/3 width): Approved Passes Awaiting Checkout */}
        <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                {isWardenOrAdmin ? 'Approved Passes' : 'My Gate Passes'}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {isWardenOrAdmin ? 'Awaiting student exit & verification' : 'Approved and upcoming travel permits'}
              </p>
            </div>
            <Link
              to="/leaves"
              className="text-xs font-semibold text-teal-600 dark:text-teal-400 hover:text-teal-700 flex items-center gap-1"
            >
              <span>All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-700/60 flex-1 overflow-y-auto max-h-[380px]">
            {approved_passes.length > 0 ? (
              approved_passes.map((pass) => (
                <div key={pass.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-teal-600 dark:text-teal-400">
                      {pass.pass_code}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                      {pass.status}
                    </span>
                  </div>
                  {isWardenOrAdmin && (
                    <p className="text-sm font-semibold text-slate-900 dark:text-white mt-1">
                      {pass.student?.name || 'Student'}
                    </p>
                  )}
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {pass.leave_type} &rarr; <span className="font-medium text-slate-700 dark:text-slate-300">{pass.destination}</span>
                  </p>
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-2">
                    <Clock className="w-3 h-3" />
                    <span>Departs: {new Date(pass.departure_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">No active passes awaiting checkout.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;
