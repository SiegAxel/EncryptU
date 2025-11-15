'use client';

import React, { useState } from 'react';
import { FiDownload, FiFileText, FiTable, FiCalendar, FiFilter } from 'react-icons/fi';

interface ReportGeneratorProps {
  type: 'users' | 'tickets';
  title: string;
  description: string;
}

interface ReportFilters {
  startDate: string;
  endDate: string;
  format: 'pdf' | 'excel';
  role?: string;
  status?: string;
  priority?: string;
  assignedTo?: string;
}

export default function ReportGenerator({ type, title, description }: ReportGeneratorProps) {
  const [filters, setFilters] = useState<ReportFilters>({
    startDate: '',
    endDate: '',
    format: 'pdf',
    role: '',
    status: '',
    priority: '',
    assignedTo: ''
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const generateReport = async () => {
    setIsGenerating(true);
    try {
      const params = new URLSearchParams();
      
      // Add format
      params.append('format', filters.format);
      
      // Add date filters
      if (filters.startDate) params.append('startDate', filters.startDate);
      if (filters.endDate) params.append('endDate', filters.endDate);
      
      // Add type-specific filters
      if (type === 'users') {
        if (filters.role) params.append('role', filters.role);
      } else if (type === 'tickets') {
        if (filters.status) params.append('status', filters.status);
        if (filters.priority) params.append('priority', filters.priority);
        if (filters.assignedTo) params.append('assignedTo', filters.assignedTo);
      }

      const endpoint = type === 'users' 
        ? '/api/admin/reports/users' 
        : '/api/support/reports/tickets';

      const response = await fetch(`${endpoint}?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      // Get the blob from response
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Set filename based on format and date
      const date = new Date().toISOString().split('T')[0];
      const filename = `${type}-report-${date}.${filters.format}`;
      a.download = filename;
      
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const resetFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      format: 'pdf',
      role: '',
      status: '',
      priority: '',
      assignedTo: ''
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <FiFileText className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
        >
          <FiFilter className="h-4 w-4" />
          <span>Filters</span>
        </button>
      </div>

      {showFilters && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Format
              </label>
              <select
                value={filters.format}
                onChange={(e) => setFilters({ ...filters, format: e.target.value as 'pdf' | 'excel' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
              </select>
            </div>

            {/* Type-specific filters */}
            {type === 'users' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={filters.role}
                  onChange={(e) => setFilters({ ...filters, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Roles</option>
                  <option value="admin">Admin</option>
                  <option value="soporte">Support</option>
                  <option value="usuario">User</option>
                </select>
              </div>
            )}

            {type === 'tickets' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Status</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={filters.priority}
                    onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Priorities</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assigned To
                  </label>
                  <select
                    value={filters.assignedTo}
                    onChange={(e) => setFilters({ ...filters, assignedTo: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Agents</option>
                    <option value="me">Assigned to Me</option>
                    <option value="unassigned">Unassigned</option>
                  </select>
                </div>
              </>
            )}
          </div>

          <div className="mt-4 flex justify-end space-x-3">
            <button
              onClick={resetFilters}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Reset Filters
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {filters.format === 'pdf' ? (
              <FiFileText className="h-5 w-5 text-red-600" />
            ) : (
              <FiTable className="h-5 w-5 text-green-600" />
            )}
            <span className="text-sm text-gray-600">
              Format: {filters.format.toUpperCase()}
            </span>
          </div>
          
          {(filters.startDate || filters.endDate) && (
            <div className="flex items-center space-x-2">
              <FiCalendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {filters.startDate && filters.endDate
                  ? `${filters.startDate} to ${filters.endDate}`
                  : filters.startDate
                  ? `From ${filters.startDate}`
                  : `Until ${filters.endDate}`}
              </span>
            </div>
          )}
        </div>

        <button
          onClick={generateReport}
          disabled={isGenerating}
          className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md transition-colors"
        >
          {isGenerating ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          ) : (
            <FiDownload className="h-4 w-4" />
          )}
          <span>{isGenerating ? 'Generating...' : 'Generate Report'}</span>
        </button>
      </div>
    </div>
  );
}