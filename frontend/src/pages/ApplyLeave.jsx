import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Calendar,
  MapPin,
  Phone,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  Compass,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { formatErrorMessage } from '../utils/errorHandler';

export const ApplyLeave = () => {
  const navigate = useNavigate();
  const { user, isWardenOrAdmin } = useAuth();

  useEffect(() => {
    if (isWardenOrAdmin) {
      navigate('/leaves', { replace: true });
    }
  }, [isWardenOrAdmin, navigate]);

  const [leaveType, setLeaveType] = useState('Weekend outing');
  const [departureDate, setDepartureDate] = useState('');
  const [returnDate, setReturnDate] = useState('');
  const [destination, setDestination] = useState('');
  const [reason, setReason] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('+91 98450 12345');
  const [parentConsent, setParentConsent] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [generatedPassCode, setGeneratedPassCode] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!departureDate || !returnDate) {
      setError('Please select both departure and return dates/times.');
      return;
    }
    if (!destination.trim()) {
      setError('Please enter your destination address or city.');
      return;
    }
    if (!reason.trim()) {
      setError('Please provide a reason for your out-station exit.');
      return;
    }
    if (!emergencyContact.trim()) {
      setError('Please provide an emergency contact phone number.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await api.post('/leaves', {
        leave_type: leaveType,
        departure_date: new Date(departureDate).toISOString(),
        return_date: new Date(returnDate).toISOString(),
        destination: destination.trim(),
        reason: reason.trim(),
        emergency_contact: emergencyContact.trim(),
        parent_consent: parentConsent,
      });

      setGeneratedPassCode(res.data?.pass_code || 'GP-2026');
      setSuccess(true);
      setTimeout(() => {
        navigate('/leaves');
      }, 2000);
    } catch (err) {
      setError(formatErrorMessage(err, 'Failed to submit leave application.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-6">
      {/* Top Breadcrumb/Back */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Gate Passes</span>
          </button>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Out-Station Leave / Gate Pass
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Apply for temporary exit and generate a verifiable gate pass code
          </p>
        </div>
      </div>

      {success ? (
        <div className="p-8 rounded-2xl bg-white dark:bg-slate-800 border border-emerald-200 dark:border-emerald-800 shadow-sm text-center space-y-3">
          <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Gate Pass Application Submitted!
          </h3>
          <p className="text-xs text-slate-500">
            Pass Code: <strong className="font-mono text-teal-600 dark:text-teal-400 text-sm">{generatedPassCode}</strong>
          </p>
          <p className="text-xs text-slate-400">
            Awaiting warden authorization. Redirecting to leave tracking...
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/80 p-6 sm:p-8 shadow-sm">
          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Leave Type (Matches C9 Hostelos_image7.jpeg) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Leave Type:
              </label>
              <div className="grid grid-cols-3 gap-3">
                {['Weekend outing', 'Emergency leave', 'Vacation'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setLeaveType(type)}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      leaveType === type
                        ? 'bg-teal-600 text-white border-teal-700 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Departure & Return Date/Time Pickers */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Departure Date & Time:
                </label>
                <input
                  type="datetime-local"
                  value={departureDate}
                  onChange={(e) => setDepartureDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Expected Return Date & Time:
                </label>
                <input
                  type="datetime-local"
                  value={returnDate}
                  onChange={(e) => setReturnDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
                />
              </div>
            </div>

            {/* Destination */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Destination (City / Full Address):
              </label>
              <div className="relative">
                <MapPin className="w-3.5 h-3.5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="e.g., Bangalore, Karnataka or Home Address"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            {/* Reason for Leave (with 0/300 character counter) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Reason for Leave:
                </label>
                <span className="text-[11px] font-mono text-slate-400">
                  {reason.length}/300
                </span>
              </div>
              <textarea
                rows="3"
                maxLength={300}
                placeholder="Explain the reason for leaving campus..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
              ></textarea>
            </div>

            {/* Emergency Contact */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Parent / Emergency Contact Phone:
              </label>
              <div className="relative">
                <Phone className="w-3.5 h-3.5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            {/* Parent Consent Toggle (Matches C9 Hostelos_image7.jpeg) */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="w-5 h-5 text-teal-600 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    Parent / Guardian Consent
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Parents have been notified and authorized this travel
                  </p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={parentConsent}
                onChange={(e) => setParentConsent(e.target.checked)}
                className="w-4 h-4 text-teal-600 rounded focus:ring-teal-500"
              />
            </div>

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs sm:text-sm font-bold shadow-md shadow-teal-900/20 transition-all disabled:opacity-50"
              >
                {loading ? 'Submitting request...' : 'Apply for gate pass'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ApplyLeave;
