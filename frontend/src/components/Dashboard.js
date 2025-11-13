import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import CasesList from './CasesList';
import CaseDetail from './CaseDetail';
import ConversationsList from './ConversationsList';
import { API_URL } from '../config';

function Dashboard({ employee, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentView, setCurrentView] = useState('cases');
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  // Parse URL to determine current view
  useEffect(() => {
    const path = location.pathname;
    if (path.includes('/cases/') && path.split('/').length > 3) {
      const caseId = path.split('/')[3];
      setCurrentView('case-detail');
      setSelectedCaseId(caseId);
    } else if (path.includes('/cases')) {
      setCurrentView('cases');
      setSelectedCaseId(null);
    } else if (path.includes('/conversations')) {
      setCurrentView('conversations');
      setSelectedCaseId(null);
    }
  }, [location]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/chatbot/dashboard/stats/`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleViewChange = (view) => {
    setCurrentView(view);
    setSelectedCaseId(null);
    if (view === 'cases') {
      navigate('/dashboard/cases');
    } else if (view === 'conversations') {
      navigate('/dashboard/conversations');
    }
  };

  const handleCaseSelect = (caseId) => {
    setSelectedCaseId(caseId);
    setCurrentView('case-detail');
    navigate(`/dashboard/cases/${caseId}`);
  };

  const handleBackToCases = () => {
    setCurrentView('cases');
    setSelectedCaseId(null);
    navigate('/dashboard/cases');
  };

  const handleLogout = () => {
    localStorage.removeItem('employee');
    onLogout();
    navigate('/');
  };

  return (
    <div className="h-screen flex bg-white">
      {/* Sidebar */}
      <div className="w-64 bg-black text-white flex flex-col border-r border-gray-200">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">ClaimIt</h1>
          <p className="text-sm text-gray-400 mt-1">Caseworker Dashboard</p>
        </div>

        {/* Stats Cards */}
        <div className="p-4 space-y-3">
          {stats && (
            <>
              <div className="bg-gray-900 rounded-lg p-3 border border-gray-800">
                <div className="text-2xl font-bold">{stats.total_cases}</div>
                <div className="text-xs text-gray-400">Total Cases</div>
              </div>
              <div className="bg-red-900 bg-opacity-30 border border-red-800 rounded-lg p-3">
                <div className="text-2xl font-bold text-red-300">{stats.high_urgency_cases}</div>
                <div className="text-xs text-red-400">High Urgency</div>
              </div>
              <div className="bg-orange-900 bg-opacity-30 border border-orange-800 rounded-lg p-3">
                <div className="text-2xl font-bold text-orange-300">{stats.emergency_cases}</div>
                <div className="text-xs text-orange-400">Emergency</div>
              </div>
              <div className="bg-blue-900 bg-opacity-30 border border-blue-800 rounded-lg p-3">
                <div className="text-2xl font-bold text-blue-300">{stats.total_conversations}</div>
                <div className="text-xs text-blue-400">Conversations</div>
              </div>
            </>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => handleViewChange('cases')}
            className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${
              currentView === 'cases' || currentView === 'case-detail'
                ? 'bg-white text-black'
                : 'text-gray-400 hover:bg-gray-900 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Cases
          </button>

          <button
            onClick={() => handleViewChange('conversations')}
            className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${
              currentView === 'conversations'
                ? 'bg-white text-black'
                : 'text-gray-400 hover:bg-gray-900 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            Conversations
          </button>
        </nav>

        {/* User Info & Logout */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center mb-3">
            <div className="bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center mr-3">
              <span className="text-sm font-semibold">
                {employee.full_name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{employee.full_name}</div>
              <div className="text-xs text-gray-400 capitalize">{employee.role.replace('_', ' ')}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 px-4 rounded-lg text-sm transition-colors flex items-center justify-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-gray-50">
        {currentView === 'cases' && <CasesList onCaseSelect={handleCaseSelect} />}
        {currentView === 'case-detail' && selectedCaseId && (
          <CaseDetail caseId={selectedCaseId} onBack={handleBackToCases} />
        )}
        {currentView === 'conversations' && <ConversationsList />}
      </div>
    </div>
  );
}

export default Dashboard;
