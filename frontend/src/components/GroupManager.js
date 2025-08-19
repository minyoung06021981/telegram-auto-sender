import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const GroupManager = () => {
  const { API, currentSession, addNotification } = useContext(AppContext);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [newGroup, setNewGroup] = useState({
    identifier: ''
  });
  const [bulkGroups, setBulkGroups] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/groups`);
      setGroups(response.data);
    } catch (error) {
      addNotification('Gagal memuat grup', 'error');
    }
    setLoading(false);
  };

  const handleAddGroup = async (e) => {
    e.preventDefault();
    
    if (!newGroup.identifier.trim()) {
      addNotification('Masukkan identifier grup', 'error');
      return;
    }
    
    try {
      await axios.post(`${API}/groups/single`, {
        identifier: newGroup.identifier
      }, {
        params: { session_id: currentSession.session_id }
      });
      
      setNewGroup({ identifier: '' });
      setShowAddModal(false);
      loadGroups();
      addNotification('Grup berhasil ditambahkan', 'success');
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Gagal menambah grup', 'error');
    }
  };

  const handleBulkAdd = async (e) => {
    e.preventDefault();
    
    if (!bulkGroups.trim()) {
      addNotification('Masukkan daftar grup', 'error');
      return;
    }
    
    const identifiers = bulkGroups.split('\n').map(line => line.trim()).filter(line => line);
    
    if (identifiers.length === 0) {
      addNotification('Tidak ada grup yang valid untuk ditambahkan', 'error');
      return;
    }
    
    try {
      const response = await axios.post(`${API}/groups/bulk`, {
        identifiers: identifiers
      }, {
        params: { session_id: currentSession.session_id }
      });
      
      const results = response.data;
      let message = '';
      
      if (results.added.length > 0) {
        message += `${results.added.length} grup berhasil ditambahkan. `;
      }
      
      if (results.skipped.length > 0) {
        message += `${results.skipped.length} grup dilewati (sudah ada). `;
      }
      
      if (results.errors.length > 0) {
        message += `${results.errors.length} grup gagal ditambahkan.`;
        
        // Show first few errors
        const errorDetails = results.errors.slice(0, 3).map(err => 
          `${err.identifier}: ${err.error}`
        ).join(', ');
        
        addNotification(`${message} Error: ${errorDetails}`, 'warning');
      } else {
        addNotification(message, 'success');
      }
      
      setBulkGroups('');
      setShowBulkModal(false);
      loadGroups();
      
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Gagal menambah grup secara bulk', 'error');
    }
  };

  const handleDeleteGroup = async (groupId) => {
    if (!window.confirm('Hapus grup ini?')) return;
    
    try {
      await axios.delete(`${API}/groups/${groupId}`);
      loadGroups();
      addNotification('Grup berhasil dihapus', 'success');
    } catch (error) {
      addNotification('Gagal menghapus grup', 'error');
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      active: { color: 'green', text: 'Aktif' },
      inactive: { color: 'gray', text: 'Non-aktif' },
      blacklisted_temp: { color: 'yellow', text: 'Blacklist Sementara' },
      blacklisted_perm: { color: 'red', text: 'Blacklist Permanen' }
    };
    
    const statusInfo = statusMap[status] || { color: 'gray', text: status };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        statusInfo.color === 'green' ? 'bg-green-100 text-green-800' :
        statusInfo.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
        statusInfo.color === 'red' ? 'bg-red-100 text-red-800' :
        'bg-gray-100 text-gray-800'
      }`}>
        {statusInfo.text}
      </span>
    );
  };

  const filteredGroups = groups.filter(group => {
    if (filter === 'all') return true;
    return group.status === filter;
  });

  const AddGroupModal = () => (
    <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Tambah Grup Baru</h2>
          <button
            onClick={() => setShowAddModal(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleAddGroup} className="space-y-6">
          <div className="form-field">
            <label className="form-label">Username Grup / ID Grup / Link Undangan</label>
            <div className="form-input-icon">
              <input
                type="text"
                value={newGroup.identifier}
                onChange={e => setNewGroup({...newGroup, identifier: e.target.value})}
                className="form-input"
                placeholder="@namagroup atau -1001234567890 atau https://t.me/+xxxxxxxxxxxxx"
                required
              />
              <svg className="icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-700">
              <strong>Tips:</strong> Masukkan salah satu dari: Username grup (@namagroup), ID Grup (-1001234567890), atau Link Undangan (https://t.me/+xxxxx). 
              Aplikasi akan memvalidasi grup sebelum menambahkan.
            </p>
          </div>

          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Tambah Grup
            </button>
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="btn-secondary"
            >
              Batal
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const BulkAddModal = () => (
    <div className="modal-overlay" onClick={() => setShowBulkModal(false)}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Tambah Banyak Grup Sekaligus</h2>
          <button
            onClick={() => setShowBulkModal(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleBulkAdd} className="space-y-4">
          <div>
            <label className="form-label">Daftar Grup (Satu Baris Satu Grup)</label>
            <textarea
              value={bulkGroups}
              onChange={e => setBulkGroups(e.target.value)}
              className="form-input h-40"
              placeholder={`@grup1
-1001234567890
https://t.me/+xxxxxxxxxxxxx
@grup2
-1005678901234`}
              required
            />
          </div>

          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-700">
              <strong>Format:</strong> Masukkan satu identifier per baris. Bisa kombinasi username (@namagroup), ID Grup (-1001234567890), 
              atau Link Undangan (https://t.me/+xxxxx). Aplikasi akan memproses semua dan memberikan laporan hasilnya.
            </p>
          </div>

          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Tambah Semua Grup
            </button>
            <button
              type="button"
              onClick={() => setShowBulkModal(false)}
              className="btn-secondary"
            >
              Batal
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Manajemen Grup</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Kelola grup dan channel target untuk pengiriman pesan
          </p>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={() => setShowBulkModal(true)}
            className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
          >
            Bulk Add
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Tambah Grup
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="dashboard-card text-center">
          <div className="text-2xl font-bold text-blue-600">{groups.length}</div>
          <div className="text-sm text-gray-600">Total Grup</div>
        </div>
        <div className="dashboard-card text-center">
          <div className="text-2xl font-bold text-green-600">
            {groups.filter(g => g.status === 'active').length}
          </div>
          <div className="text-sm text-gray-600">Aktif</div>
        </div>
        <div className="dashboard-card text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {groups.filter(g => g.status === 'blacklisted_temp').length}
          </div>
          <div className="text-sm text-gray-600">Blacklist Sementara</div>
        </div>
        <div className="dashboard-card text-center">
          <div className="text-2xl font-bold text-red-600">
            {groups.filter(g => g.status === 'blacklisted_perm').length}
          </div>
          <div className="text-sm text-gray-600">Blacklist Permanen</div>
        </div>
      </div>

      {/* Filters */}
      <div className="dashboard-card">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Semua ({groups.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'active'
                ? 'bg-green-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Aktif ({groups.filter(g => g.status === 'active').length})
          </button>
          <button
            onClick={() => setFilter('blacklisted_temp')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'blacklisted_temp'
                ? 'bg-yellow-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Blacklist Sementara ({groups.filter(g => g.status === 'blacklisted_temp').length})
          </button>
          <button
            onClick={() => setFilter('blacklisted_perm')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'blacklisted_perm'
                ? 'bg-red-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Blacklist Permanen ({groups.filter(g => g.status === 'blacklisted_perm').length})
          </button>
        </div>
      </div>

      {/* Groups Table */}
      <div className="dashboard-card">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="loading-spinner"></div>
          </div>
        ) : filteredGroups.length === 0 ? (
          <div className="text-center py-8">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
              {filter === 'all' ? 'Belum ada grup' : `Tidak ada grup dengan filter "${filter}"`}
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {filter === 'all' 
                ? 'Tambahkan grup pertama Anda untuk mulai mengirim pesan otomatis.'
                : 'Coba ubah filter untuk melihat grup lainnya.'
              }
            </p>
            {filter === 'all' && (
              <button
                onClick={() => setShowAddModal(true)}
                className="btn-primary mt-4"
              >
                Tambah Grup Pertama
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nama</th>
                  <th>Username/ID</th>
                  <th>Status</th>
                  <th>Alasan Blacklist</th>
                  <th>Ditambahkan</th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {filteredGroups.map((group) => (
                  <tr key={group.id}>
                    <td className="font-medium">{group.name || 'Tidak ada nama'}</td>
                    <td>
                      <div className="space-y-1">
                        {group.username && (
                          <div className="text-blue-600">@{group.username}</div>
                        )}
                        <div className="text-gray-500 text-sm">ID: {group.group_id}</div>
                      </div>
                    </td>
                    <td>{getStatusBadge(group.status)}</td>
                    <td>
                      {group.blacklist_reason ? (
                        <span className="text-red-600 text-sm">{group.blacklist_reason}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="text-sm text-gray-500">
                      {new Date(group.created_at).toLocaleDateString('id-ID')}
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeleteGroup(group.id)}
                        className="btn-danger"
                        title="Hapus grup"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modals */}
      {showAddModal && <AddGroupModal />}
      {showBulkModal && <BulkAddModal />}
    </div>
  );
};

export default GroupManager;