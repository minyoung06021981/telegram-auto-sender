import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const UserAuth = () => {
  const { API, addNotification } = useContext(AppContext);
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/users/login`, {
        username: formData.username,
        password: formData.password
      });
      
      // Store token and user data
      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('userData', JSON.stringify(response.data.user));
      
      // Redirect to main app
      window.location.href = '/dashboard';
      
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Login gagal', 'error');
    }
    
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      addNotification('Password tidak cocok', 'error');
      return;
    }
    
    if (formData.password.length < 6) {
      addNotification('Password minimal 6 karakter', 'error');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/users/register`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName
      });
      
      // Store token and user data
      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('userData', JSON.stringify(response.data.user));
      
      addNotification('Registrasi berhasil!', 'success');
      
      // Redirect to main app
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1000);
      
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Registrasi gagal', 'error');
    }
    
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-r from-telegram-blue to-telegram-accent rounded-full flex items-center justify-center mx-auto mb-6 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"></div>
            <svg className="w-10 h-10 text-white z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-telegram-blue to-telegram-accent bg-clip-text text-transparent mb-3">
            Telegram Auto Sender
          </h1>
          <p className="text-gray-600 text-lg">
            {isLogin ? 'Masuk ke akun Anda' : 'Buat akun baru'}
          </p>
        </div>

        {/* Login/Register Toggle */}
        <div className="flex mb-8 p-1 bg-gray-100 rounded-xl">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
              isLogin
                ? 'bg-white text-telegram-blue shadow-md transform scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Masuk
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
              !isLogin
                ? 'bg-white text-telegram-blue shadow-md transform scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Daftar
          </button>
        </div>

        {/* Login Form */}
        {isLogin && (
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="form-field">
              <label className="form-label">Username</label>
              <div className="form-input-icon">
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Masukkan username Anda"
                  required
                />
                <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">Password</label>
              <div className="form-input-icon">
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Masukkan password Anda"
                  required
                />
                <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full text-lg py-4 mt-8"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="loading-spinner mr-3"></div>
                  Masuk...
                </div>
              ) : (
                'Masuk'
              )}
            </button>
          </form>
        )}

        {/* Register Form */}
        {!isLogin && (
          <form onSubmit={handleRegister} className="space-y-6">
            <div>
              <label className="form-label">Nama Lengkap</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Masukkan nama lengkap Anda"
                required
              />
            </div>

            <div>
              <label className="form-label">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Pilih username unik"
                required
              />
            </div>

            <div>
              <label className="form-label">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Masukkan email Anda"
                required
              />
            </div>

            <div>
              <label className="form-label">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Buat password (min. 6 karakter)"
                required
                minLength={6}
              />
            </div>

            <div>
              <label className="form-label">Konfirmasi Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Ulangi password Anda"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full text-lg py-4"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="loading-spinner mr-3"></div>
                  Mendaftar...
                </div>
              ) : (
                'Buat Akun'
              )}
            </button>
          </form>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-sm text-gray-500 text-center space-y-2">
            <p>✨ Fitur Premium: Unlimited Groups & Messages</p>
            <p>🔐 Keamanan Tingkat Enterprise</p>
            <p>🚀 Auto Sender dengan AI Scheduling</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserAuth;