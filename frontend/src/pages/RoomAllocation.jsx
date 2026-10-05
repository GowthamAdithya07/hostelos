import React, { useState, useEffect } from 'react';
import {
  DoorClosed,
  Search,
  Filter,
  UserPlus,
  LogOut,
  CheckCircle,
  Building,
  Sparkles,
  Users,
  Shield,
  X,
  AlertCircle,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { formatErrorMessage } from '../utils/errorHandler';

export const RoomAllocation = () => {
  const { isWardenOrAdmin } = useAuth();

  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBlock, setSelectedBlock] = useState('All Blocks');
  const [selectedType, setSelectedType] = useState('All Types');
  const [selectedAc, setSelectedAc] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Allocation Modal State
  const [allocModalOpen, setAllocModalOpen] = useState(false);
  const [targetRoom, setTargetRoom] = useState(null);
  const [unallocatedStudents, setUnallocatedStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [allocating, setAllocating] = useState(false);
  const [allocError, setAllocError] = useState('');

  const fetchRooms = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedBlock !== 'All Blocks') params.block = selectedBlock;
      if (selectedType !== 'All Types') params.room_type = selectedType;
      if (selectedAc !== 'All') params.has_ac = selectedAc === 'AC';
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const res = await api.get('/rooms', { params });
      setRooms(res.data || []);
    } catch (err) {
      console.error('Failed to load rooms:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
  }, [selectedBlock, selectedType, selectedAc, searchQuery]);

  const openAllocateModal = async (room) => {
    setTargetRoom(room);
    setAllocError('');
    setSelectedStudentId('');
    setAllocModalOpen(true);
    try {
      const res = await api.get('/rooms/students/unallocated');
      setUnallocatedStudents(res.data || []);
    } catch (err) {
      console.error('Failed to fetch unallocated students:', err);
    }
  };

  const handleAllocate = async (e) => {
    e.preventDefault();
    if (!selectedStudentId) {
      setAllocError('Please select a student to allocate.');
      return;
    }
    setAllocating(true);
    setAllocError('');
    try {
      await api.post('/rooms/allocate', {
        room_id: targetRoom.id,
        student_id: parseInt(selectedStudentId),
      });
      setAllocModalOpen(false);
      fetchRooms();
    } catch (err) {
      setAllocError(formatErrorMessage(err, 'Failed to allocate bed.'));
    } finally {
      setAllocating(false);
    }
  };

  const handleDeallocate = async (studentId) => {
    if (!window.confirm('Are you sure you want to checkout/vacate this student from this bed?')) return;
    try {
      await api.post('/rooms/deallocate', {
        room_id: 0,
        student_id: studentId,
      });
      fetchRooms();
    } catch (err) {
      alert(formatErrorMessage(err, 'Failed to vacate bed.'));
    }
  };

  const totalBeds = rooms.reduce((acc, r) => acc + r.capacity, 0);
  const occupiedBeds = rooms.reduce((acc, r) => acc + r.occupied_count, 0);
  const vacantBeds = totalBeds - occupiedBeds;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Room Allocation
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Visual room cards with bed status (🔴 Occupied / 🟢 Vacant) across Blocks A, B, and C
          </p>
        </div>

        {/* Live Summary Counter Pills */}
        <div className="flex items-center gap-2">
          <div className="px-3 py-1.5 rounded-lg bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800/60 text-teal-800 dark:text-teal-300 text-xs font-semibold">
            Occupied: <strong className="font-bold">{occupiedBeds}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300 text-xs font-semibold">
            Vacant: <strong className="font-bold">{vacantBeds}</strong>
          </div>
        </div>
      </div>

      {/* FILTER BAR (Matches C9 Hostelos_image2.jpeg) */}
      <div className="p-4 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Block Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
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

        {/* Dropdown Filters & Search */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Room Type */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-2.5 py-1.5 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="All Types">All Types</option>
            <option value="Single">Single</option>
            <option value="Double">Double</option>
          </select>

          {/* AC Status */}
          <select
            value={selectedAc}
            onChange={(e) => setSelectedAc(e.target.value)}
            className="px-2.5 py-1.5 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="All">All AC/Non-AC</option>
            <option value="AC">AC</option>
            <option value="Non-AC">Non-AC</option>
          </select>

          {/* Search Box */}
          <div className="relative min-w-[200px] flex-1">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search room or student..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl text-xs bg-slate-100 dark:bg-slate-700/60 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>
        </div>
      </div>

      {/* ROOMS GRID (Matches C9 Hostelos_image2.jpeg) */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : rooms.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm font-semibold text-slate-500">No rooms found matching your filter criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {rooms.map((room) => {
            const isFull = room.vacant_count === 0;

            return (
              <div
                key={room.id}
                className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  {/* Room Card Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700/60">
                    <div>
                      <span className="text-lg font-extrabold text-slate-900 dark:text-white font-mono">
                        {room.room_number}
                      </span>
                      <p className="text-[11px] text-slate-400 font-medium">{room.block}</p>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                        {room.room_type} · {room.has_ac ? 'AC' : 'Non-AC'}
                      </span>
                    </div>
                  </div>

                  {/* Bed Indicator Dots */}
                  <div className="py-3 flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                      Beds ({room.occupied_count}/{room.capacity})
                    </span>
                    <div className="flex items-center gap-1.5">
                      {room.beds?.map((b) => (
                        <span
                          key={b.bed_index}
                          title={b.is_occupied ? `Bed ${b.bed_index}: Occupied by ${b.student?.name}` : `Bed ${b.bed_index}: Vacant`}
                          className={`w-3.5 h-3.5 rounded-full ${
                            b.is_occupied ? 'bg-rose-500' : 'bg-emerald-500'
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Occupants Details */}
                  <div className="space-y-2 my-2">
                    {room.occupants && room.occupants.length > 0 ? (
                      room.occupants.map((student) => (
                        <div
                          key={student.id}
                          className="p-2 rounded-xl bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs"
                        >
                          <div className="min-w-0 pr-1">
                            <p className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                              {student.name}
                            </p>
                            <p className="text-[10px] text-slate-400 font-mono truncate">
                              {student.roll_number || 'Resident'}
                            </p>
                          </div>
                          {isWardenOrAdmin && (
                            <button
                              onClick={() => handleDeallocate(student.id)}
                              title="Checkout / Vacate bed"
                              className="text-slate-400 hover:text-rose-500 p-1 transition-colors"
                            >
                              <LogOut className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 italic py-2">Room currently vacant.</p>
                    )}
                  </div>
                </div>

                {/* Allocate Action Button */}
                {isWardenOrAdmin && (
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-700/60">
                    <button
                      onClick={() => openAllocateModal(room)}
                      disabled={isFull}
                      className={`w-full py-1.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors ${
                        isFull
                          ? 'bg-slate-100 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                          : 'bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800 text-teal-700 dark:text-teal-300 hover:bg-teal-100 dark:hover:bg-teal-900/60'
                      }`}
                    >
                      <UserPlus className="w-3.5 h-3.5" />
                      <span>{isFull ? 'Room Full' : '+ Allocate Bed'}</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* BED ALLOCATION MODAL */}
      {allocModalOpen && targetRoom && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Allocate Bed: Room {targetRoom.room_number}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {targetRoom.block} · {targetRoom.room_type} ({targetRoom.vacant_count} beds free)
                </p>
              </div>
              <button
                onClick={() => setAllocModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {allocError && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{allocError}</span>
              </div>
            )}

            <form onSubmit={handleAllocate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Select Unallocated Student:
                </label>
                <select
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">-- Choose student --</option>
                  {unallocatedStudents.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.roll_number || s.email})
                    </option>
                  ))}
                </select>
                {unallocatedStudents.length === 0 && (
                  <p className="text-[11px] text-slate-400 mt-1 italic">
                    All students are currently allocated rooms.
                  </p>
                )}
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setAllocModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={allocating || !selectedStudentId}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white shadow-sm transition-colors disabled:opacity-50"
                >
                  {allocating ? 'Allocating...' : 'Confirm Bed Allocation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoomAllocation;
