import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { API_URL } from '../config';

function CasesList({ onCaseSelect }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('urgency_score');
  const [order, setOrder] = useState('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCases, setFilteredCases] = useState([]);

  useEffect(() => {
    fetchCases();
  }, [sortBy, order]);

  useEffect(() => {
    // Client-side filtering based on search term
    if (searchTerm.trim()) {
      const filtered = cases.filter(c => 
        c.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.phone_number?.includes(searchTerm)
      );
      setFilteredCases(filtered);
    } else {
      setFilteredCases(cases);
    }
  }, [searchTerm, cases]);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/chatbot/dashboard/cases/?sort_by=${sortBy}&order=${order}`
      );
      const data = await response.json();
      setCases(data.cases || []);
      setFilteredCases(data.cases || []);
    } catch (error) {
      console.error('Error fetching cases:', error);
      setCases([]);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (score) => {
    if (score >= 8) return 'bg-red-50 text-red-900 border-red-200';
    if (score >= 6) return 'bg-orange-50 text-orange-900 border-orange-200';
    if (score >= 4) return 'bg-yellow-50 text-yellow-900 border-yellow-200';
    return 'bg-green-50 text-green-900 border-green-200';
  };

  const getUrgencyLabel = (score) => {
    if (score >= 8) return 'Critical';
    if (score >= 6) return 'High';
    if (score >= 4) return 'Medium';
    return 'Low';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Cases</h1>
        <p className="text-gray-600 mt-1">Manage and review submitted cases</p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap gap-4">
        {/* Search */}
        <div className="flex-1 min-w-[300px]">
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name, email, or phone..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none"
            />
            <svg className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Sort Controls */}
        <div className="flex gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black outline-none bg-white"
          >
            <option value="urgency_score">Urgency</option>
            <option value="submitted_at">Date Submitted</option>
            <option value="full_name">Name</option>
          </select>

          <button
            onClick={() => setOrder(order === 'asc' ? 'desc' : 'asc')}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title={order === 'asc' ? 'Sort descending' : 'Sort ascending'}
          >
            <svg className={`w-5 h-5 transition-transform ${order === 'asc' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <button
            onClick={fetchCases}
            className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {filteredCases.length} of {cases.length} cases
      </div>

      {/* Cases List */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
        </div>
      ) : filteredCases.length === 0 ? (
        <Card className="p-12 text-center border border-gray-200">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No cases found</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Try adjusting your search criteria' : 'Cases will appear here once clients complete the intake process'}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredCases.map((caseItem) => (
            <Card
              key={caseItem.id}
              onClick={() => onCaseSelect(caseItem.id)}
              className="p-6 hover:shadow-md transition-all cursor-pointer border border-gray-200 bg-white"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {caseItem.full_name || 'Unknown'}
                    </h3>
                    <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getUrgencyColor(caseItem.urgency_score)}`}>
                      {getUrgencyLabel(caseItem.urgency_score)} - {caseItem.urgency_score}/10
                    </span>
                    {caseItem.has_emergency_needs && (
                      <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-red-600 text-white">
                        EMERGENCY
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                    <div className="flex items-center text-gray-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {caseItem.email || 'No email'}
                    </div>
                    <div className="flex items-center text-gray-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {caseItem.phone_number || 'No phone'}
                    </div>
                  </div>

                  {caseItem.urgency_reasoning && (
                    <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                      <span className="font-medium">Urgency Reason:</span> {caseItem.urgency_reasoning}
                    </p>
                  )}

                  {caseItem.recommended_programs && caseItem.recommended_programs.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs text-gray-600 font-medium">Recommended Programs:</span>
                      {caseItem.recommended_programs.slice(0, 3).map((program, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs border border-gray-200">
                          {program}
                        </span>
                      ))}
                      {caseItem.recommended_programs.length > 3 && (
                        <span className="text-xs text-gray-500">+{caseItem.recommended_programs.length - 3} more</span>
                      )}
                    </div>
                  )}
                </div>

                <div className="text-right ml-4">
                  <div className="text-sm text-gray-500 mb-2">
                    {formatDate(caseItem.submitted_at)}
                  </div>
                  <div className="text-xs text-gray-400">
                    Age: {caseItem.age || 'N/A'}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default CasesList;
