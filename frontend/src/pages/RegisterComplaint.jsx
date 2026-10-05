import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileText,
  X,
  Plus,
  ArrowLeft,
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { formatErrorMessage } from '../utils/errorHandler';

export const RegisterComplaint = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [category, setCategory] = useState('Plumbing');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState('Medium');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be under 5MB.');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Please provide a complaint title.');
      return;
    }
    if (!description.trim()) {
      setError('Please describe the issue in detail.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      let imageUrl = null;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        const uploadRes = await api.post('/complaints/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        imageUrl = uploadRes.data?.image_url;
      }

      await api.post('/complaints', {
        category,
        title: title.trim(),
        description: description.trim(),
        urgency,
        image_url: imageUrl,
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/complaints');
      }, 1500);
    } catch (err) {
      setError(formatErrorMessage(err, 'Failed to submit complaint.'));
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
            <span>Back to Complaints</span>
          </button>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Register Complaint
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Submit a maintenance or facility issue to hostel administration
          </p>
        </div>
      </div>

      {success ? (
        <div className="p-8 rounded-2xl bg-white dark:bg-slate-800 border border-emerald-200 dark:border-emerald-800 shadow-sm text-center space-y-3">
          <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Complaint Registered Successfully!
          </h3>
          <p className="text-xs text-slate-500">
            A maintenance ticket number has been generated and dispatched to the hostel administration.
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
            {/* Category */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Category:
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
              >
                <option value="Plumbing">Plumbing (Washbasin, Taps, Drainage)</option>
                <option value="Electrical & Lighting">Electrical & Lighting (Fans, Lights, Switches)</option>
                <option value="Internet Connectivity">Internet Connectivity (Wi-Fi, LAN)</option>
                <option value="Carpentry / Furniture">Carpentry / Furniture (Doors, Locks, Desks)</option>
                <option value="Housekeeping">Housekeeping (Cleaning, Waste Disposal)</option>
                <option value="Other">Other Issues</option>
              </select>
            </div>

            {/* Title with VARCHAR(50) Character Counter (Matches root_screenshot.png) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Issue Title:
                </label>
                <span className="text-[11px] font-mono text-slate-400">
                  {title.length}/50 — VARCHAR(50)
                </span>
              </div>
              <input
                type="text"
                maxLength={50}
                placeholder="e.g., Bathroom tap leaking continuously"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            {/* Description with TEXT(400) Character Counter (Matches root_screenshot.png) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Detailed Description:
                </label>
                <span className="text-[11px] font-mono text-slate-400">
                  {description.length}/400 — TEXT
                </span>
              </div>
              <textarea
                rows="4"
                maxLength={400}
                placeholder="Explain the issue clearly (location, severity, when it started)..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
              ></textarea>
            </div>

            {/* Urgency Selection */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Urgency Level:
              </label>
              <div className="grid grid-cols-3 gap-3">
                {['Low', 'Medium', 'High'].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setUrgency(lvl)}
                    className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                      urgency === lvl
                        ? lvl === 'High'
                          ? 'bg-rose-500 text-white border-rose-600 shadow-sm'
                          : lvl === 'Medium'
                          ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                          : 'bg-blue-500 text-white border-blue-600 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            {/* Image / Attachment Upload (Matches root_screenshot.png) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Photo Evidence / Attachment (Optional):
              </label>
              <div className="relative border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-6 text-center hover:border-teal-500/80 transition-colors bg-slate-50/50 dark:bg-slate-900/50">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                />
                <div className="flex flex-col items-center justify-center pointer-events-none">
                  <div className="w-10 h-10 rounded-full bg-teal-50 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-2">
                    <UploadCloud className="w-5 h-5" />
                  </div>
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Click to upload image or drag and drop
                  </p>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    PNG, JPG, WEBP up to 5MB
                  </p>
                </div>
              </div>

              {previewUrl && (
                <div className="mt-3 relative inline-block">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-24 h-24 object-cover rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl('');
                    }}
                    className="absolute -top-2 -right-2 p-1 bg-rose-500 text-white rounded-full shadow hover:bg-rose-600 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="pt-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs sm:text-sm font-bold shadow-md shadow-teal-900/20 transition-all disabled:opacity-50"
              >
                {loading ? 'Submitting ticket...' : 'Submit complaint'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default RegisterComplaint;
