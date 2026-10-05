import React, { useState, useEffect } from 'react';
import {
  CalendarCheck2,
  Download,
  CheckCircle2,
  Clock,
  Search,
  Filter,
  Users,
  AlertCircle,
  FileSpreadsheet,
} from 'lucide-react';
import api, { API_BASE_URL } from '../api/axios';
import { useAuth } from '../context/AuthContext';

export const AttendanceRegister = () => {
  const { isWardenOrAdmin } = useAuth();

  const [dateStr, setDateStr] = useState(() => new Date().toISOString().split('T')[0]);
  const [selectedBlock, setSelectedBlock] = useState('All Blocks');
  const [searchQuery, setSearchQuery] = useState('');
  const [roster, setRoster] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState('');

  const fetchRoster = async () => {
    try {
      setLoading(true);
      const params = { date: dateStr };
      if (selectedBlock !== 'All Blocks') params.block = selectedBlock;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const res = await api.get('/attendance', { params });
      setRoster(res.data || []);
    } catch (err) {
      console.error('Failed to load attendance roster:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoster();
  }, [dateStr, selectedBlock, searchQuery]);

  const handleMarkStatus = async (studentId, status) => {
    try {
      await api.post('/attendance/mark', {
        student_id: studentId,
        date: dateStr,
        status: status,
      });

      // Optimistically update local roster
      setRoster((prev) =>
        prev.map((r) => (r.student_id === studentId ? { ...r, status: status } : r))
      );
    } catch (err) {
      alert('Failed to mark attendance.');
    }
  };

  const handleBulkMarkPresent = async () => {
    if (!window.confirm(`Mark all residents in ${selectedBlock} as 'Present' for ${dateStr}?`)) return;
    try {
      const res = await api.post('/attendance/bulk', {
        date: dateStr,
        block: selectedBlock === 'All Blocks' ? null : selectedBlock,
        status: 'Present',
      });
      setActionMessage(res.data?.message || 'Updated successfully.');
      setTimeout(() => setActionMessage(''), 3000);
      fetchRoster();
    } catch (err) {
      alert('Failed to execute bulk mark.');
    }
  };

  const handleExportCsv = () => {
    const url = `${API_BASE_URL}/attendance/export?date=${dateStr}${
      selectedBlock !== 'All Blocks' ? `&block=${encodeURIComponent(selectedBlock)}` : ''
    }`;
    window.open(url, '_blank');
  };

  // Counts
  const presentCount = roster.filter((r) => r.status === 'Present').length;
  const absentCount = roster.filter((r) => r.status === 'Absent').length;
  const lateCount = roster.filter((r) => r.status === 'Late / Permitted').length;
  const totalStudents = roster.length;
  const presentPct = totalStudents > 0 ? Math.round((presentCount / totalStudents) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Daily Attendance Register
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Night roll-call verification, status toggling, and gate pass reconciliation
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {isWardenOrAdmin && (
            <button
              onClick={handleBulkMarkPresent}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800 text-teal-700 dark:text-teal-300 text-xs font-semibold hover:bg-teal-100 transition-colors shadow-sm"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Bulk Mark Present</span>
            </button>
          )}

          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* FILTER & DATE CONTROLS (Matches C9 Hostelos_image4.jpeg) */}
      <div className="p-4 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Date Selector & Block Pills */}
        <div className="flex items-center gap-3 flex-wrap">
          <input
            type="date"
            value={dateStr}
            onChange={(e) => setDateStr(e.target.value)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-white border border-slate-200 dark:border-slate-600 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />

          <div className="flex items-center gap-1.5 overflow-x-auto">
            {['All Blocks', 'Block A', 'Block B', 'Block C'].map((blk) => (
              <button
                key={blk}
                onClick={() => setSelectedBlock(blk)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                  selectedBlock === blk
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                {blk}
              </button>
            ))}
          </div>
        </div>

        {/* Live Attendance Stats & Search */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-xs font-medium">
            <span className="text-emerald-600 font-bold">{presentCount} Present ({presentPct}%)</span>
            <span className="text-slate-300 dark:text-slate-600">|</span>
            <span className="text-rose-500 font-bold">{absentCount} Absent</span>
            <span className="text-slate-300 dark:text-slate-600">|</span>
            <span className="text-amber-500 font-bold">{lateCount} Late</span>
          </div>

          <div className="relative min-w-[180px]">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search resident..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-100 dark:bg-slate-700/60 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>
        </div>
      </div>

      {/* ROSTER TABLE (Matches C9 Hostelos_image4.jpeg) */}
      <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : roster.length === 0 ? (
          <div className="p-12 text-center text-sm font-semibold text-slate-500">
            No students found in the selected block or filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700/80 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Room & Block</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4 text-center">Night Roll-Call Status</th>
                  <th className="py-3 px-4">Notes / Gate Pass Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
                {roster.map((record) => (
                  <tr key={record.student_id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                    {/* Room & Block */}
                    <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-white">
                      {record.room_number} <span className="text-[10px] text-slate-400 font-sans font-normal">({record.block})</span>
                    </td>

                    {/* Student Name */}
                    <td className="py-3 px-4 font-semibold text-slate-800 dark:text-slate-200">
                      {record.student_name}
                    </td>

                    {/* Roll Number */}
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                      {record.roll_number || 'N/A'}
                    </td>

                    {/* Toggle Buttons (Present, Absent, Late / Permitted) */}
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => handleMarkStatus(record.student_id, 'Present')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            record.status === 'Present'
                              ? 'bg-emerald-600 text-white shadow-sm'
                              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                          }`}
                        >
                          Present
                        </button>

                        <button
                          onClick={() => handleMarkStatus(record.student_id, 'Absent')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            record.status === 'Absent'
                              ? 'bg-rose-600 text-white shadow-sm'
                              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                          }`}
                        >
                          Absent
                        </button>

                        <button
                          onClick={() => handleMarkStatus(record.student_id, 'Late / Permitted')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            record.status === 'Late / Permitted'
                              ? 'bg-amber-500 text-white shadow-sm'
                              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                          }`}
                        >
                          Late / Permitted
                        </button>
                      </div>
                    </td>

                    {/* Notes */}
                    <td className="py-3 px-4 text-slate-500 text-[11px]">
                      {record.notes ? (
                        <span className="italic text-amber-600 dark:text-amber-400">{record.notes}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
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

export default AttendanceRegister;
