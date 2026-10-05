import React from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('RecoverEase UI Error Caught:', error, errorInfo);
  }

  handleReset = () => {
    localStorage.clear();
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full border border-slate-200 shadow-xl text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-8 h-8" />
            </div>

            <h2 className="text-xl font-bold text-slate-900">Something went wrong</h2>
            <p className="text-sm text-slate-500">
              An unexpected UI error occurred. Resetting session data will restore application state.
            </p>

            <div className="p-3 bg-slate-50 rounded-xl text-xs font-mono text-slate-600 text-left overflow-x-auto max-h-24">
              {this.state.error?.message || 'Unknown error'}
            </div>

            <div className="pt-2 flex flex-col gap-2">
              <button
                onClick={this.handleReset}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl flex items-center justify-center gap-2 shadow-sm transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset Cache & Reload</span>
              </button>

              <button
                onClick={() => (window.location.href = '/')}
                className="w-full py-2 px-4 border border-slate-200 text-slate-700 text-sm font-semibold rounded-xl hover:bg-slate-50 transition-colors"
              >
                Go to Homepage
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
