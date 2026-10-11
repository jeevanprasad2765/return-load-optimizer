import React from 'react';
import { Navbar } from './Navbar';

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
          <span>&copy; 2026 Empty Return Load Optimizer — Open Source Freight Optimization Engine</span>
          <span className="text-slate-400 font-medium">Tamil Nadu Express Freight Corridor Demo</span>
        </div>
      </footer>
    </div>
  );
};
