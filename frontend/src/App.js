import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './components/Chat';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';
import { Analytics } from '@vercel/analytics/react';
import { API_URL } from './config';

function App() {
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedEmployee = localStorage.getItem('employee');
    if (storedEmployee) {
      try {
        setEmployee(JSON.parse(storedEmployee));
      } catch (error) {
        console.error('Error parsing stored employee:', error);
        localStorage.removeItem('employee');
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (employeeData) => {
    setEmployee(employeeData);
  };

  const handleLogout = () => {
    setEmployee(null);
  };

  // Client-facing chat route
  const ChatRoute = () => {
    const [localConvId, setLocalConvId] = useState(null);

    useEffect(() => {
      // Check if there's an existing conversation in localStorage
      const existingConvId = localStorage.getItem('currentConversationId');
      if (existingConvId) {
        setLocalConvId(existingConvId);
      }
    }, []);

    const createNewConversation = async () => {
      try {
        const response = await fetch(`${API_URL}/chatbot/conversations/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        const newConvId = data.id;
        setLocalConvId(newConvId);
        localStorage.setItem('currentConversationId', newConvId);
        return newConvId;
      } catch (error) {
        console.error('Error creating conversation:', error);
        return null;
      }
    };

    return (
      <div className="h-screen w-screen overflow-hidden">
        <Chat conversationId={localConvId} onCreateConversation={createNewConversation} />
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Client-facing chat interface */}
        <Route path="/chat" element={<ChatRoute />} />
        
        {/* Employee login */}
        <Route 
          path="/login" 
          element={
            employee ? <Navigate to="/dashboard/cases" /> : <Login onLoginSuccess={handleLoginSuccess} />
          } 
        />
        
        {/* Dashboard routes - protected */}
        <Route 
          path="/dashboard/*" 
          element={
            employee ? (
              <Dashboard employee={employee} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" />
            )
          } 
        />
        
        {/* Default redirect based on auth status */}
        <Route 
          path="/" 
          element={
            employee ? <Navigate to="/dashboard/cases" /> : <Navigate to="/chat" />
          } 
        />
      </Routes>
      <Analytics />
    </Router>
  );
}

export default App;
