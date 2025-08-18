import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const Settings = () => {
  const { API, addNotification, theme, setTheme } = useContext(AppContext);
  const [settings, setSettings] = useState({
    min_message_interval: 5,
    max_message_interval: 15,
    min_cycle_interval: 60,
    max_cycle_interval: 120,
    max_retry_attempts: 3,
    is_scheduler_active: false,
    theme: 'auto',
    notifications_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/settings`);
      setSettings(response.data);
    } catch (error) {
      addNotification('Gagal memuat pengaturan', 'error');
    }
    setLoading(false);
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await axios.put(`${API}/settings`, settings);
      addNotification('Pengaturan berhasil disimpan', 'success');
    } catch (error) {
      addNotification('Gagal menyimpan pengaturan', 'error');
    }
    
    setSaving(false);
  };

  const handleInputChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    handleInputChange('theme', newTheme);
    
    // Apply theme immediately
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (newTheme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      // Auto theme
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const SettingCard = ({ title, description, children }) => (
    <div className="dashboard-card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm">{description}</p>
      </div>
      {children}
    </div>
  );

  const InputField = ({ label, type = "number", value, onChange, min, max, suffix }) => (
    <div>
      <label className="form-label">{label}</label>
      <div className="flex items-center space-x-2">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? parseInt(e.target.value) || 0 : e.target.value)}
          className="form-input"
          min={min}
          max={max}
        />
        {suffix && <span className="text-sm text-gray-500">{suffix}</span>}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Pengaturan</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Konfigurasi perilaku aplikasi dan preferensi
          </p>
        </div>
      </div>

      <form onSubmit={handleSaveSettings} className="space-y-6">
        {/* Scheduler Settings */}
        <SettingCard
          title="Pengaturan Scheduler"
          description="Kontrol timing dan perilaku pengiriman pesan otomatis"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              label="Interval Pesan Minimum"
              value={settings.min_message_interval}
              onChange={(val) => handleInputChange('min_message_interval', val)}
              min={1}
              max={60}
              suffix="detik"
            />
            
            <InputField
              label="Interval Pesan Maksimum"
              value={settings.max_message_interval}
              onChange={(val) => handleInputChange('max_message_interval', val)}
              min={settings.min_message_interval || 1}
              max={120}
              suffix="detik"
            />
            
            <InputField
              label="Interval Siklus Minimum"
              value={settings.min_cycle_interval}
              onChange={(val) => handleInputChange('min_cycle_interval', val)}
              min={10}
              max={1440}
              suffix="menit"
            />
            
            <InputField
              label="Interval Siklus Maksimum"
              value={settings.max_cycle_interval}
              onChange={(val) => handleInputChange('max_cycle_interval', val)}
              min={settings.min_cycle_interval || 10}
              max={1440}
              suffix="menit"
            />
            
            <InputField
              label="Maksimum Retry"
              value={settings.max_retry_attempts}
              onChange={(val) => handleInputChange('max_retry_attempts', val)}
              min={1}
              max={10}
              suffix="kali"
            />
          </div>

          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              <strong>Tips:</strong> Interval yang lebih random membantu menghindari deteksi spam. 
              Gunakan interval yang wajar agar tidak melanggar Terms of Service Telegram.
            </p>
          </div>
        </SettingCard>

        {/* Theme Settings */}
        <SettingCard
          title="Tampilan"
          description="Kustomisasi tema dan preferensi visual aplikasi"
        >
          <div>
            <label className="form-label">Tema</label>
            <div className="grid grid-cols-3 gap-3">
              {['light', 'dark', 'auto'].map((themeOption) => (
                <button
                  key={themeOption}
                  type="button"
                  onClick={() => handleThemeChange(themeOption)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    settings.theme === themeOption
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-center mb-2">
                    {themeOption === 'light' && (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    )}
                    {themeOption === 'dark' && (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                      </svg>
                    )}
                    {themeOption === 'auto' && (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    )}
                  </div>
                  <div className="text-sm font-medium capitalize">{themeOption}</div>
                </button>
              ))}
            </div>
          </div>
        </SettingCard>

        {/* Notification Settings */}
        <SettingCard
          title="Notifikasi"
          description="Kontrol notifikasi dan pemberitahuan sistem"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-800 dark:text-white">Notifikasi Real-time</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Terima notifikasi untuk hasil pengiriman pesan dan status sistem
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications_enabled}
                  onChange={(e) => handleInputChange('notifications_enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </SettingCard>

        {/* Advanced Settings */}
        <SettingCard
          title="Pengaturan Lanjutan"
          description="Konfigurasi tingkat lanjut untuk pengguna berpengalaman"
        >
          <div className="space-y-4">
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div>
                  <h4 className="font-medium text-yellow-800 dark:text-yellow-200">Perhatian</h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Pengaturan ini dapat mempengaruhi performa dan kepatuhan terhadap Terms of Service Telegram. 
                    Ubah hanya jika Anda memahami konsekuensinya.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-800 dark:text-white mb-3">Export/Import Konfigurasi</h4>
                <div className="space-y-2">
                  <button
                    type="button"
                    className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm"
                  >
                    Export Konfigurasi
                  </button>
                  <button
                    type="button"
                    className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm"
                  >
                    Import Konfigurasi
                  </button>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-800 dark:text-white mb-3">Data Management</h4>
                <div className="space-y-2">
                  <button
                    type="button"
                    className="w-full px-4 py-2 bg-red-100 hover:bg-red-200 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg transition-colors text-sm"
                  >
                    Hapus Semua Log
                  </button>
                  <button
                    type="button"
                    className="w-full px-4 py-2 bg-red-100 hover:bg-red-200 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg transition-colors text-sm"
                  >
                    Reset Blacklist
                  </button>
                </div>
              </div>
            </div>
          </div>
        </SettingCard>

        {/* Save Button */}
        <div className="sticky bottom-6">
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary px-8 py-3"
            >
              {saving ? (
                <div className="flex items-center space-x-2">
                  <div className="loading-spinner w-4 h-4"></div>
                  <span>Menyimpan...</span>
                </div>
              ) : (
                'Simpan Pengaturan'
              )}
            </button>
          </div>
        </div>
      </form>

      {/* System Information */}
      <SettingCard
        title="Informasi Sistem"
        description="Detail versi dan status aplikasi"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-lg font-semibold text-gray-800 dark:text-white">v1.0.0</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Versi Aplikasi</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-lg font-semibold text-green-600">Online</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Status Backend</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-lg font-semibold text-blue-600">Aktif</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Koneksi Database</div>
          </div>
        </div>
      </SettingCard>
    </div>
  );
};

export default Settings;