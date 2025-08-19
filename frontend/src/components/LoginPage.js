import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const LoginPage = () => {
  const { API, setCurrentSession, setIsAuthenticated, sessions, loadSessions, addNotification, saveSessionToStorage, clearSessionFromStorage } = useContext(AppContext);
  
  const [step, setStep] = useState('select'); // select, new, verify
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    api_id: '',
    api_hash: '',
    phone_number: '',
    phone_code: '',
    password: ''
  });
  const [sessionData, setSessionData] = useState(null);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleNewLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/login`, {
        api_id: parseInt(formData.api_id),
        api_hash: formData.api_hash,
        phone_number: formData.phone_number
      });
      
      setSessionData(response.data);
      
      if (response.data.authenticated) {
        // Already authenticated
        setCurrentSession(response.data);
        setIsAuthenticated(true);
        saveSessionToStorage(response.data);
        addNotification('Login berhasil!', 'success');
      } else {
        // Need verification
        setStep('verify');
      }
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Login gagal', 'error');
    }
    
    setLoading(false);
  };

  const handleVerification = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const requestData = {
        session_id: sessionData.session_id,
        phone_number: formData.phone_number
      };
      
      // Add phone_code if provided and not requires_password yet
      if (formData.phone_code && !sessionData?.requires_password) {
        requestData.phone_code = formData.phone_code;
      }
      
      // Add password if this is a 2FA step
      if (sessionData?.requires_password && formData.password) {
        requestData.password = formData.password;
      }
      
      const response = await axios.post(`${API}/auth/verify`, requestData);
      
      if (response.data.requires_password) {
        // Update session data to show password field
        setSessionData(response.data);
        addNotification('Masukkan password 2FA Anda', 'info');
      } else if (response.data.authenticated) {
        setCurrentSession(response.data);
        setIsAuthenticated(true);
        saveSessionToStorage(response.data);
        addNotification('Login berhasil!', 'success');
        loadSessions(); // Refresh sessions list
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Verifikasi gagal';
      addNotification(errorMsg, 'error');
      console.error('Verification error:', error);
    }
    
    setLoading(false);
  };

  const handleExistingSession = async (sessionId) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/load-session/${sessionId}`);
      setCurrentSession(response.data);
      setIsAuthenticated(true);
      saveSessionToStorage(response.data);
      addNotification('Session dimuat berhasil!', 'success');
    } catch (error) {
      addNotification('Session expired atau tidak valid', 'error');
      clearSessionFromStorage();
    }
    
    setLoading(false);
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Hapus session ini?')) return;
    
    try {
      await axios.delete(`${API}/auth/session/${sessionId}`);
      loadSessions();
      addNotification('Session dihapus', 'success');
    } catch (error) {
      addNotification('Gagal menghapus session', 'error');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Telegram Auto Sender</h1>
          <p className="text-gray-600">Masuk ke akun Telegram Anda</p>
        </div>

        {step === 'select' && (
          <div className="space-y-4">
            {sessions.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Session Tersimpan</h3>
                <div className="space-y-2">
                  {sessions.map((session) => (
                    <div key={session.session_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {session.user_info?.first_name?.[0] || 'U'}
                        </div>
                        <div>
                          <div className="font-medium">
                            {session.user_info?.first_name} {session.user_info?.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {session.phone_number}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleExistingSession(session.session_id)}
                          disabled={loading}
                          className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 disabled:opacity-50"
                        >
                          Gunakan
                        </button>
                        <button
                          onClick={() => handleDeleteSession(session.session_id)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          Hapus
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-center mt-4">
                  <button
                    onClick={() => setStep('new')}
                    className="text-blue-500 hover:text-blue-600 font-medium"
                  >
                    Atau buat login baru
                  </button>
                </div>
              </div>
            )}

            {sessions.length === 0 && (
              <div className="text-center">
                <button
                  onClick={() => setStep('new')}
                  className="btn-primary w-full"
                >
                  Login dengan Akun Baru
                </button>
              </div>
            )}
          </div>
        )}

        {step === 'new' && (
          <form onSubmit={handleNewLogin} className="space-y-6">
            <div className="form-field">
              <label className="form-label">API ID</label>
              <div className="form-input-icon">
                <input
                  type="text"
                  name="api_id"
                  value={formData.api_id}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Masukkan API ID dari my.telegram.org"
                  required
                />
                <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v-2H7v-2H4a1 1 0 01-1-1v-4a1 1 0 011-1h2.586l4.707-4.707C10.923 3.663 12 4.109 12 5v4.586l4.707 4.707A1 1 0 0117 15z" />
                </svg>
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">API Hash</label>
              <div className="form-input-icon">
                <input
                  type="text"
                  name="api_hash"
                  value={formData.api_hash}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Masukkan API Hash dari my.telegram.org"
                  required
                />
                <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">Nomor Telepon</label>
              <div className="form-input-icon">
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="+62812345678"
                  required
                />
                <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full mt-8"
            >
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Kirim Kode Verifikasi'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setStep('select')}
                className="text-gray-500 hover:text-gray-600"
              >
                Kembali
              </button>
            </div>
          </form>
        )}

        {step === 'verify' && (
          <form onSubmit={handleVerification} className="space-y-4">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold">Verifikasi</h3>
              {!sessionData?.requires_password ? (
                <p className="text-gray-600">
                  Kode verifikasi telah dikirim ke {formData.phone_number}
                </p>
              ) : (
                <p className="text-gray-600">
                  Masukkan password 2FA untuk menyelesaikan login
                </p>
              )}
            </div>

            {!sessionData?.requires_password && (
              <div>
                <label className="form-label">Kode Verifikasi</label>
                <input
                  type="text"
                  name="phone_code"
                  value={formData.phone_code}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="12345"
                  maxLength="5"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Masukkan 5 digit kode yang dikirim ke Telegram
                </p>
              </div>
            )}

            {sessionData?.requires_password && (
              <div>
                <label className="form-label">Password 2FA</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Password 2FA Anda"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Masukkan password dua faktor yang Anda set di Telegram
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="loading-spinner mr-2"></div>
                  Memverifikasi...
                </div>
              ) : (
                sessionData?.requires_password ? 'Masuk dengan 2FA' : 'Verifikasi Kode'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setStep('new');
                  setSessionData(null);
                  setFormData({
                    api_id: '',
                    api_hash: '',
                    phone_number: '',
                    phone_code: '',
                    password: ''
                  });
                }}
                className="text-gray-500 hover:text-gray-600"
              >
                Kembali
              </button>
            </div>
          </form>
        )}

        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center space-y-1">
            <p>Dapatkan API ID dan Hash dari:</p>
            <a
              href="https://my.telegram.org/apps"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-600"
            >
              my.telegram.org/apps
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;