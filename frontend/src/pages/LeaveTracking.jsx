import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  CheckCircle2,
  XCircle,
  Clock,
  Filter,
  Search,
  Plus,
  ShieldCheck,
  UserCheck,
  Phone,
  Calendar,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { formatErrorMessage } from '../utils/errorHandler';

export const LeaveTracking = () => {
  const { user, isWardenOrAdmin } = useAuth();

  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');
  const [leaveTypeFilter, setLeaveTypeFilter] = useState('All Types');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchLeaves = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter !== 'All') params.status = statusFilter;
      if (leaveTypeFilter !== 'All Types') params.leave_type = leaveTypeFilter;
      if (!isWardenOrAdmin) params.only_mine = true;

      const res = await api.get('/leaves', { params });
      setLeaves(res.data || []);
    } catch (err) {
      console.error('Failed to load leaves:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves();
  }, [statusFilter, leaveTypeFilter]);

  const handleUpdateStatus = async (leaveId, newStatus) => {
    try {
      await api.patch(`/leaves/${leaveId}/status`, {
        status: newStatus,
      });
      fetchLeaves();
    } catch (err) {
      alert(formatErrorMessage(err, 'Failed to update gate pass status.'));
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Approved':
      case 'Validated':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30';
      case 'Rejected':
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30';
      case 'Checked Out':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/30';
      default:
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30';
    }
  };

  const filteredLeaves = leaves.filter((l) => {
    if (!searchQuery.trim()) return true;
    const term = searchQuery.toLowerCase();
    return (
      l.pass_code.toLowerCase().includes(term) ||
      (l.student?.name || '').toLowerCase().includes(term) ||
      l.destination.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            {isWardenOrAdmin ? 'Gate Passes & Leave Tracking' : 'My Gate Passes'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            {isWardenOrAdmin
              ? 'Monitor and authorize student out-station permits and hostel checkouts'
              : 'View and track your submitted out-station permits and travel approvals'}
          </p>
        </div>

        {!isWardenOrAdmin && (
          <Link
            to="/apply-leave"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Apply for leave</span>
          </Link>
        )}
      </div>

      {/* FILTER CONTROLS */}
      <div className="p-4 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Status Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {['All', 'Pending', 'Approved', 'Validated', 'Rejected'].map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                statusFilter === tab
                  ? 'bg-teal-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {tab === 'All' ? 'All passes' : tab}
            </button>
          ))}
        </div>

        {/* Search & Leave Type */}
        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={leaveTypeFilter}
            onChange={(e) => setLeaveTypeFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="All Types">All Leave Types</option>
            <option value="Weekend outing">Weekend outing</option>
            <option value="Emergency leave">Emergency leave</option>
            <option value="Vacation">Vacation</option>
          </select>

          <div className="relative min-w-[200px] flex-1">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search pass code or student..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-100 dark:bg-slate-700/60 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>
        </div>
      </div>

      {/* GATE PASSES TABLE */}
      <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredLeaves.length === 0 ? (
          <div className="p-12 text-center text-sm font-semibold text-slate-500">
            No gate passes found matching your criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700/80 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Pass Code</th>
                  {isWardenOrAdmin && <th className="py-3 px-4">Student & Room</th>}
                  <th className="py-3 px-4">Leave Type</th>
                  <th className="py-3 px-4">Destination & Reason</th>
                  <th className="py-3 px-4">Departure & Return</th>
                  <th className="py-3 px-4">Status</th>
                  {isWardenOrAdmin && <th className="py-3 px-4 text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
                {filteredLeaves.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                    {/* Pass Code */}
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-600 dark:text-teal-400">
                      {l.pass_code}
                    </td>

                    {/* Student & Room */}
                    {isWardenOrAdmin && (
                      <td className="py-3.5 px-4">
                        <p className="font-semibold text-slate-800 dark:text-slate-200">
                          {l.student?.name || 'Student'}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono">
                          Room {l.student?.room_number || 'A-101'}
                        </p>
                      </td>
                    )}

                    {/* Leave Type */}
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium">
                        {l.leave_type}
                      </span>
                    </td>

                    {/* Destination & Reason */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <p className="font-semibold text-slate-900 dark:text-white truncate">
                        {l.destination}
                      </p>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                        {l.reason}
                      </p>
                    </td>

                    {/* Dates */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-500">
                      <div>
                        Out: {new Date(l.departure_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        In: {new Date(l.return_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                      </div>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[11px] ${getStatusBadge(l.status)}`}>
                        {l.status}
                      </span>
                    </td>

                    {/* Warden / Admin Actions */}
                    {isWardenOrAdmin && (
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {l.status === 'Pending' && (
                            <>
                              <button
                                onClick={() => handleUpdateStatus(l.id, 'Approved')}
                                className="px-2.5 py-1 rounded-lg bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 hover:bg-teal-100 font-semibold text-[11px] border border-teal-200 dark:border-teal-800"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleUpdateStatus(l.id, 'Rejected')}
                                className="px-2.5 py-1 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 hover:bg-rose-100 font-semibold text-[11px] border border-rose-200 dark:border-rose-800"
                              >
                                Reject
                              </button>
                            </>
                          )}
                          {l.status === 'Approved' && (
                            <button
                              onClick={() => handleUpdateStatus(l.id, 'Validated')}
                              className="px-2.5 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 font-semibold text-[11px] border border-emerald-200 dark:border-emerald-800"
                            >
                              Validate Exit
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaveTracking;
