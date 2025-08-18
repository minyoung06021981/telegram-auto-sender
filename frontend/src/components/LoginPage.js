import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const LoginPage = () => {
  const { API, setCurrentSession, setIsAuthenticated, sessions, loadSessions, addNotification } = useContext(AppContext);
  
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
      const response = await axios.post(`${API}/auth/verify`, {
        session_id: sessionData.session_id,
        phone_code: formData.phone_code,
        password: formData.password
      });
      
      if (response.data.requires_password) {
        setSessionData(response.data);
        // Stay on verify step, show password field
      } else if (response.data.authenticated) {
        setCurrentSession(response.data);
        setIsAuthenticated(true);
        addNotification('Login berhasil!', 'success');
        loadSessions(); // Refresh sessions list
      }
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Verifikasi gagal', 'error');
    }
    
    setLoading(false);
  };

  const handleExistingSession = async (sessionId) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/load-session/${sessionId}`);
      setCurrentSession(response.data);
      setIsAuthenticated(true);
      addNotification('Session dimuat berhasil!', 'success');
    } catch (error) {
      addNotification('Session expired atau tidak valid', 'error');
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
          <form onSubmit={handleNewLogin} className="space-y-4">
            <div>
              <label className="form-label">API ID</label>
              <input
                type="text"
                name="api_id"
                value={formData.api_id}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Masukkan API ID dari my.telegram.org"
                required
              />
            </div>

            <div>
              <label className="form-label">API Hash</label>
              <input
                type="text"
                name="api_hash"
                value={formData.api_hash}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Masukkan API Hash dari my.telegram.org"
                required
              />
            </div>

            <div>
              <label className="form-label">Nomor Telepon</label>
              <input
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                className="form-input"
                placeholder="+62812345678"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
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
              <p className="text-gray-600">
                Kode verifikasi telah dikirim ke {formData.phone_number}
              </p>
            </div>

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
                required={!sessionData?.requires_password}
              />
            </div>

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
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Verifikasi'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setStep('new')}
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