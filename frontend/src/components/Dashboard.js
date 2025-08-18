import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const Dashboard = () => {
  const { API, currentSession, addNotification, socket } = useContext(AppContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [schedulerActive, setSchedulerActive] = useState(false);
  const [logs, setLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
      setSchedulerActive(response.data.scheduler.active);
    } catch (error) {
      addNotification('Gagal memuat data dashboard', 'error');
    }
    setLoading(false);
  };

  const toggleScheduler = async () => {
    try {
      const endpoint = schedulerActive ? 'stop' : 'start';
      await axios.post(`${API}/scheduler/${endpoint}`, {}, {
        params: { session_id: currentSession.session_id }
      });
      
      setSchedulerActive(!schedulerActive);
      addNotification(
        schedulerActive ? 'Scheduler dihentikan' : 'Scheduler dimulai',
        'success'
      );
      
      // Reload stats to get updated info
      loadDashboardData();
    } catch (error) {
      addNotification('Gagal mengubah status scheduler', 'error');
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <div className={`stat-card ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium opacity-90">{title}</h3>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs opacity-75 mt-1">{subtitle}</p>
          )}
        </div>
        <div className="text-3xl opacity-80">
          {icon}
        </div>
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
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Selamat datang kembali, {currentSession?.user_info?.first_name}!
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <button
            onClick={toggleScheduler}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              schedulerActive
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {schedulerActive ? 'Stop Scheduler' : 'Start Scheduler'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Grup"
            value={stats.groups.total}
            color="blue"
            icon="🏢"
          />
          <StatCard
            title="Grup Aktif"
            value={stats.groups.active}
            color="green"
            icon="✅"
          />
          <StatCard
            title="Pesan Terkirim"
            value={stats.messages.sent_24h}
            color="orange"
            subtitle="24 jam terakhir"
            icon="📤"
          />
          <StatCard
            title="Pesan Gagal"
            value={stats.messages.failed_24h}
            color="red"
            subtitle="24 jam terakhir"
            icon="❌"
          />
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scheduler Status */}
        <div className="dashboard-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Status Scheduler
            </h2>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              schedulerActive
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
            }`}>
              {schedulerActive ? 'Aktif' : 'Non-aktif'}
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Status:</span>
              <span className="font-medium">
                {schedulerActive ? 'Mengirim pesan otomatis' : 'Berhenti'}
              </span>
            </div>
            
            {stats && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Grup tersedia:</span>
                  <span className="font-medium">{stats.groups.active}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Grup di-blacklist:</span>
                  <span className="font-medium">
                    {stats.groups.temp_blacklisted + stats.groups.perm_blacklisted}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Group Overview */}
        <div className="dashboard-card">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
            Ringkasan Grup
          </h2>
          
          {stats && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Aktif</span>
                </div>
                <span className="font-medium">{stats.groups.active}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span>Blacklist Sementara</span>
                </div>
                <span className="font-medium">{stats.groups.temp_blacklisted}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span>Blacklist Permanen</span>
                </div>
                <span className="font-medium">{stats.groups.perm_blacklisted}</span>
              </div>

              {stats.groups.total > 0 && (
                <div className="pt-3 border-t dark:border-gray-600">
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Success Rate:</span>
                    <span>
                      {Math.round((stats.groups.active / stats.groups.total) * 100)}%
                    </span>
                  </div>
                  <div className="progress-bar mt-2">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${(stats.groups.active / stats.groups.total) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
          Aksi Cepat
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.href = '/groups'}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors group"
          >
            <div className="text-center">
              <svg className="w-8 h-8 mx-auto mb-2 text-gray-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <p className="font-medium">Tambah Grup</p>
              <p className="text-sm text-gray-500">Kelola grup target</p>
            </div>
          </button>
          
          <button
            onClick={() => window.location.href = '/messages'}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-green-500 dark:hover:border-green-400 transition-colors group"
          >
            <div className="text-center">
              <svg className="w-8 h-8 mx-auto mb-2 text-gray-400 group-hover:text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <p className="font-medium">Edit Template</p>
              <p className="text-sm text-gray-500">Kelola pesan otomatis</p>
            </div>
          </button>
          
          <button
            onClick={() => window.location.href = '/settings'}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-purple-500 dark:hover:border-purple-400 transition-colors group"
          >
            <div className="text-center">
              <svg className="w-8 h-8 mx-auto mb-2 text-gray-400 group-hover:text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p className="font-medium">Pengaturan</p>
              <p className="text-sm text-gray-500">Konfigurasi aplikasi</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;