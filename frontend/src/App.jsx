import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// HostelOS Pages
import Overview from './pages/Overview';
import RoomAllocation from './pages/RoomAllocation';
import ComplaintManagement from './pages/ComplaintManagement';
import RegisterComplaint from './pages/RegisterComplaint';
import AttendanceRegister from './pages/AttendanceRegister';
import LeaveTracking from './pages/LeaveTracking';
import ApplyLeave from './pages/ApplyLeave';
import Login from './pages/Login';
import Register from './pages/Register';

function MainAppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen bg-[#F8FAFC] dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden font-sans selection:bg-teal-500 selection:text-white">
      {/* Dark Teal/Slate Left Sidebar */}
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopHeader onMenuClick={() => setMobileOpen(true)} />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Routes>
            {/* Core Operations Dashboard (Matches image1.png) */}
            <Route path="/" element={<Overview />} />
            <Route path="/overview" element={<Overview />} />

            {/* Room Allocation Grid (Warden / Admin ONLY - No student access) */}
            <Route
              path="/rooms"
              element={
                <ProtectedRoute requireWardenOrAdmin>
                  <RoomAllocation />
                </ProtectedRoute>
              }
            />

            {/* Complaint Management & Tracking */}
            <Route path="/complaints" element={<ComplaintManagement />} />
            <Route path="/register-complaint" element={<RegisterComplaint />} />

            {/* Daily Attendance Roll-Call (Warden / Admin ONLY - No student access) */}
            <Route
              path="/attendance"
              element={
                <ProtectedRoute requireWardenOrAdmin>
                  <AttendanceRegister />
                </ProtectedRoute>
              }
            />

            {/* Out-Station Gate Passes */}
            <Route path="/leaves" element={<LeaveTracking />} />
            <Route
              path="/apply-leave"
              element={
                <ProtectedRoute allowedRoles={['STUDENT']}>
                  <ApplyLeave />
                </ProtectedRoute>
              }
            />

            {/* Authentication */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <MainAppShell />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
