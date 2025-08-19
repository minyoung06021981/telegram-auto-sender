import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

// Import components
import UserAuth from './components/UserAuth';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import GroupManager from './components/GroupManager';
import MessageTemplates from './components/MessageTemplates';
import Settings from './components/Settings';
import SubscriptionPage from './components/SubscriptionPage';
import Navigation from './components/Navigation';

// Context for global state
const AppContext = React.createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  // User Authentication State
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  
  // Telegram State  
  const [currentSession, setCurrentSession] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    // Load saved sessions on startup
    loadSessions();
    
    // Check for saved authentication state
    checkSavedAuth();
    
    // Initialize socket connection
    const socketConnection = io(BACKEND_URL, {
      transports: ['websocket', 'polling']
    });
    
    setSocket(socketConnection);
    
    // Listen for real-time updates
    socketConnection.on('message_results', (data) => {
      console.log('Message results received:', data);
      addNotification('Message sending completed', 'info');
    });
    
    socketConnection.on('scheduler_update', (data) => {
      console.log('Scheduler update:', data);
      addNotification(`Scheduler ${data.status}`, 'info');
    });

    return () => {
      socketConnection.disconnect();
    };
  }, []);

  const checkSavedAuth = async () => {
    try {
      const savedSession = localStorage.getItem('currentSession');
      if (savedSession) {
        const sessionData = JSON.parse(savedSession);
        
        // Validate session is still valid by testing load-session endpoint
        const response = await axios.post(`${API}/auth/load-session/${sessionData.session_id}`);
        
        if (response.data && response.data.authenticated) {
          setCurrentSession(response.data);
          setIsAuthenticated(true);
          console.log('Auto-login successful with saved session');
        }
      }
    } catch (error) {
      console.log('Saved session is invalid or expired, clearing localStorage');
      localStorage.removeItem('currentSession');
    }
  };

  const loadSessions = async () => {
    try {
      const response = await axios.get(`${API}/auth/sessions`);
      setSessions(response.data);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const saveSessionToStorage = (sessionData) => {
    localStorage.setItem('currentSession', JSON.stringify(sessionData));
  };

  const clearSessionFromStorage = () => {
    localStorage.removeItem('currentSession');
  };

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const contextValue = {
    currentSession,
    setCurrentSession,
    isAuthenticated,
    setIsAuthenticated,
    sessions,
    setSessions,
    socket,
    API,
    addNotification,
    theme,
    setTheme,
    loadSessions,
    saveSessionToStorage,
    clearSessionFromStorage
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className={`min-h-screen bg-gray-50 ${theme === 'dark' ? 'dark bg-gray-900' : ''}`}>
        <Router>
          <div className="flex h-screen">
            {isAuthenticated && (
              <div className="w-64 bg-white dark:bg-gray-800 shadow-lg">
                <Navigation />
              </div>
            )}
            
            <div className="flex-1 overflow-auto">
              {/* Notifications */}
              <div className="fixed top-4 right-4 z-50 space-y-2">
                {notifications.map(notification => (
                  <div
                    key={notification.id}
                    className={`px-4 py-2 rounded-lg shadow-lg text-white ${
                      notification.type === 'error' ? 'bg-red-500' :
                      notification.type === 'success' ? 'bg-green-500' :
                      'bg-blue-500'
                    }`}
                  >
                    {notification.message}
                  </div>
                ))}
              </div>

              <Routes>
                <Route
                  path="/login"
                  element={
                    !isAuthenticated ? (
                      <LoginPage />
                    ) : (
                      <Navigate to="/dashboard" replace />
                    )
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    isAuthenticated ? (
                      <Dashboard />
                    ) : (
                      <Navigate to="/login" replace />
                    )
                  }
                />
                <Route
                  path="/groups"
                  element={
                    isAuthenticated ? (
                      <GroupManager />
                    ) : (
                      <Navigate to="/login" replace />
                    )
                  }
                />
                <Route
                  path="/messages"
                  element={
                    isAuthenticated ? (
                      <MessageTemplates />
                    ) : (
                      <Navigate to="/login" replace />
                    )
                  }
                />
                <Route
                  path="/settings"
                  element={
                    isAuthenticated ? (
                      <Settings />
                    ) : (
                      <Navigate to="/login" replace />
                    )
                  }
                />
                <Route
                  path="/"
                  element={
                    <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
                  }
                />
              </Routes>
            </div>
          </div>
        </Router>
      </div>
    </AppContext.Provider>
  );
}

export { AppContext };
export default App;