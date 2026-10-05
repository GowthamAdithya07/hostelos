import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  Plus,
  Wrench,
  X,
  Building,
  User,
  ExternalLink,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { formatErrorMessage } from '../utils/errorHandler';

export const ComplaintManagement = () => {
  const { user, isWardenOrAdmin } = useAuth();

  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All Categories');
  const [searchQuery, setSearchQuery] = useState('');

  // Resolve Modal State
  const [resolveModalOpen, setResolveModalOpen] = useState(false);
  const [targetComplaint, setTargetComplaint] = useState(null);
  const [assignedStaff, setAssignedStaff] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter !== 'All') params.status = statusFilter;
      if (categoryFilter !== 'All Categories') params.category = categoryFilter;
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (!isWardenOrAdmin) params.only_mine = true;

      const res = await api.get('/complaints', { params });
      setComplaints(res.data || []);
    } catch (err) {
      console.error('Failed to load complaints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [statusFilter, categoryFilter, searchQuery]);

  const openResolveModal = (c) => {
    setTargetComplaint(c);
    setAssignedStaff(c.assigned_staff || '');
    setResolutionNotes(c.resolution_notes || '');
    setResolveModalOpen(true);
  };

  const handleResolveSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.patch(`/complaints/${targetComplaint.id}/status`, {
        status: 'Resolved',
        assigned_staff: assignedStaff,
        resolution_notes: resolutionNotes,
      });
      setResolveModalOpen(false);
      fetchComplaints();
    } catch (err) {
      alert(formatErrorMessage(err, 'Failed to resolve ticket.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleEscalate = async (complaintId) => {
    try {
      await api.patch(`/complaints/${complaintId}/status`, {
        status: 'Escalated',
      });
      fetchComplaints();
    } catch (err) {
      alert(formatErrorMessage(err, 'Failed to escalate ticket.'));
    }
  };

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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            {isWardenOrAdmin ? 'Complaint Management' : 'My Registered Complaints'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            {isWardenOrAdmin
              ? 'Track, assign technicians, and resolve resident facility & maintenance requests'
              : 'Track your filed maintenance requests and view technician resolution updates'}
          </p>
        </div>

        <Link
          to="/register-complaint"
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register complaint</span>
        </Link>
      </div>

      {/* FILTER & SEARCH TABS (Matches C9 Hostelos_image3.jpeg) */}
      <div className="p-4 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Status Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {['All', 'Open', 'Escalated', 'Resolved'].map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                statusFilter === tab
                  ? 'bg-teal-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {tab === 'All' ? 'All tickets' : tab}
            </button>
          ))}
        </div>

        {/* Category & Search */}
        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="All Categories">All Categories</option>
            <option value="Plumbing">Plumbing</option>
            <option value="Electrical & Lighting">Electrical & Lighting</option>
            <option value="Internet Connectivity">Internet Connectivity</option>
            <option value="Carpentry / Furniture">Carpentry / Furniture</option>
            <option value="Housekeeping">Housekeeping</option>
            <option value="Other">Other</option>
          </select>

          <div className="relative min-w-[200px] flex-1">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search ticket or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-100 dark:bg-slate-700/60 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>
        </div>
      </div>

      {/* TICKETS TABLE (Matches C9 Hostelos_image3.jpeg) */}
      <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : complaints.length === 0 ? (
          <div className="p-12 text-center text-sm font-semibold text-slate-500">
            No complaints found matching criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700/80 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Ticket</th>
                  {isWardenOrAdmin && <th className="py-3 px-4">Resident & Room</th>}
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Issue Title</th>
                  <th className="py-3 px-4">Urgency</th>
                  <th className="py-3 px-4">Date Filed</th>
                  <th className="py-3 px-4">Status</th>
                  {isWardenOrAdmin && <th className="py-3 px-4 text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
                {complaints.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                    {/* Ticket Code */}
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 dark:text-white">
                      {c.ticket_number}
                    </td>

                    {/* Resident & Room */}
                    {isWardenOrAdmin && (
                      <td className="py-3.5 px-4">
                        <p className="font-semibold text-slate-800 dark:text-slate-200">
                          {c.student?.name || 'Resident'}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono">
                          Room {c.student?.room_number || 'A-101'}
                        </p>
                      </td>
                    )}

                    {/* Category */}
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium">
                        {c.category}
                      </span>
                    </td>

                    {/* Title & Description */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <p className="font-semibold text-slate-900 dark:text-white truncate">{c.title}</p>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">{c.description}</p>
                    </td>

                    {/* Urgency */}
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${getUrgencyBadge(c.urgency)}`}>
                        {c.urgency}
                      </span>
                    </td>

                    {/* Date */}
                    <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap">
                      {new Date(c.created_at).toLocaleDateString([], {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[11px] ${getStatusBadge(c.status)}`}>
                        {c.status}
                      </span>
                    </td>

                    {/* Actions */}
                    {isWardenOrAdmin && (
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {c.status !== 'Resolved' && (
                            <>
                              <button
                                onClick={() => openResolveModal(c)}
                                className="px-2.5 py-1 rounded-lg bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 hover:bg-teal-100 font-semibold text-[11px] border border-teal-200 dark:border-teal-800"
                              >
                                Resolve
                              </button>
                              {c.status === 'Open' && (
                                <button
                                  onClick={() => handleEscalate(c.id)}
                                  className="px-2.5 py-1 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 hover:bg-purple-100 font-semibold text-[11px] border border-purple-200 dark:border-purple-800"
                                >
                                  Escalate
                                </button>
                              )}
                            </>
                          )}
                          {c.status === 'Resolved' && (
                            <span className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Done</span>
                            </span>
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

      {/* RESOLVE TICKET MODAL */}
      {resolveModalOpen && targetComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Resolve Ticket: {targetComplaint.ticket_number}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {targetComplaint.category} · {targetComplaint.title}
                </p>
              </div>
              <button
                onClick={() => setResolveModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleResolveSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Assigned Maintenance Staff / Technician:
                </label>
                <input
                  type="text"
                  placeholder="e.g., Ramesh (Plumber) / Murugan (Electrician)"
                  value={assignedStaff}
                  onChange={(e) => setAssignedStaff(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Resolution Notes / Work Done:
                </label>
                <textarea
                  rows="3"
                  placeholder="Describe parts replaced or corrective action taken..."
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                ></textarea>
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setResolveModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm"
                >
                  {submitting ? 'Resolving...' : 'Confirm Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplaintManagement;
