import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../App';

const MessageTemplates = () => {
  const { API, currentSession, addNotification } = useContext(AppContext);
  const [templates, setTemplates] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    content: '',
    is_default: false
  });
  const [sendData, setSendData] = useState({
    template_id: '',
    selected_groups: [],
    send_immediately: true
  });

  useEffect(() => {
    loadTemplates();
    loadGroups();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates`);
      setTemplates(response.data);
    } catch (error) {
      addNotification('Gagal memuat template', 'error');
    }
  };

  const loadGroups = async () => {
    try {
      const response = await axios.get(`${API}/groups`);
      setGroups(response.data.filter(g => g.status === 'active'));
    } catch (error) {
      addNotification('Gagal memuat grup', 'error');
    }
    setLoading(false);
  };

  const handleSaveTemplate = async (e) => {
    e.preventDefault();
    
    try {
      if (editingTemplate) {
        // Update existing template
        await axios.put(`${API}/templates/${editingTemplate.id}`, newTemplate);
        addNotification('Template berhasil diperbarui', 'success');
      } else {
        // Create new template
        await axios.post(`${API}/templates`, newTemplate);
        addNotification('Template berhasil dibuat', 'success');
      }
      
      setNewTemplate({ name: '', content: '', is_default: false });
      setEditingTemplate(null);
      setShowAddModal(false);
      loadTemplates();
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Gagal menyimpan template', 'error');
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Hapus template ini?')) return;
    
    try {
      await axios.delete(`${API}/templates/${templateId}`);
      loadTemplates();
      addNotification('Template berhasil dihapus', 'success');
    } catch (error) {
      addNotification('Gagal menghapus template', 'error');
    }
  };

  const handleEditTemplate = (template) => {
    setNewTemplate({
      name: template.name,
      content: template.content,
      is_default: template.is_default
    });
    setEditingTemplate(template);
    setShowAddModal(true);
  };

  const handleSendMessages = async (e) => {
    e.preventDefault();
    
    if (sendData.selected_groups.length === 0) {
      addNotification('Pilih minimal satu grup', 'error');
      return;
    }

    try {
      await axios.post(`${API}/messages/send`, {
        group_ids: sendData.selected_groups,
        message_template_id: sendData.template_id,
        send_immediately: sendData.send_immediately
      }, {
        params: { session_id: currentSession.session_id }
      });
      
      setShowSendModal(false);
      setSendData({ template_id: '', selected_groups: [], send_immediately: true });
      addNotification(
        sendData.send_immediately 
          ? 'Pesan sedang dikirim!' 
          : 'Pesan telah dijadwalkan',
        'success'
      );
    } catch (error) {
      addNotification(error.response?.data?.detail || 'Gagal mengirim pesan', 'error');
    }
  };

  const openSendModal = (templateId) => {
    setSendData({
      ...sendData,
      template_id: templateId,
      selected_groups: groups.map(g => g.group_id) // Select all by default
    });
    setShowSendModal(true);
  };

  const toggleGroupSelection = (groupId) => {
    setSendData({
      ...sendData,
      selected_groups: sendData.selected_groups.includes(groupId)
        ? sendData.selected_groups.filter(id => id !== groupId)
        : [...sendData.selected_groups, groupId]
    });
  };

  const TemplateModal = () => (
    <div className="modal-overlay" onClick={() => {
      setShowAddModal(false);
      setEditingTemplate(null);
      setNewTemplate({ name: '', content: '', is_default: false });
    }}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">
            {editingTemplate ? 'Edit Template' : 'Template Baru'}
          </h2>
          <button
            onClick={() => {
              setShowAddModal(false);
              setEditingTemplate(null);
              setNewTemplate({ name: '', content: '', is_default: false });
            }}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSaveTemplate} className="space-y-4">
          <div>
            <label className="form-label">Nama Template</label>
            <input
              type="text"
              value={newTemplate.name}
              onChange={e => setNewTemplate({...newTemplate, name: e.target.value})}
              className="form-input"
              placeholder="Nama untuk identifikasi template"
              required
            />
          </div>

          <div>
            <label className="form-label">Isi Pesan</label>
            <textarea
              value={newTemplate.content}
              onChange={e => setNewTemplate({...newTemplate, content: e.target.value})}
              className="form-input h-32 resize-none"
              placeholder="Ketik pesan yang akan dikirim secara otomatis..."
              required
            />
            <div className="text-sm text-gray-500 mt-1">
              Panjang: {newTemplate.content.length} karakter
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_default"
              checked={newTemplate.is_default}
              onChange={e => setNewTemplate({...newTemplate, is_default: e.target.checked})}
              className="rounded border-gray-300"
            />
            <label htmlFor="is_default" className="text-sm text-gray-700">
              Jadikan sebagai template default
            </label>
          </div>

          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              {editingTemplate ? 'Perbarui' : 'Simpan'} Template
            </button>
            <button
              type="button"
              onClick={() => {
                setShowAddModal(false);
                setEditingTemplate(null);
                setNewTemplate({ name: '', content: '', is_default: false });
              }}
              className="btn-secondary"
            >
              Batal
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const SendModal = () => (
    <div className="modal-overlay" onClick={() => {
      setShowSendModal(false);
      setSendData({ template_id: '', selected_groups: [], send_immediately: true });
    }}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Kirim Pesan ke Grup</h2>
          <button
            onClick={() => {
              setShowSendModal(false);
              setSendData({ template_id: '', selected_groups: [], send_immediately: true });
            }}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSendMessages} className="space-y-4">
          <div>
            <label className="form-label">Preview Pesan</label>
            <div className="bg-gray-50 p-3 rounded-lg border">
              {templates.find(t => t.id === sendData.template_id)?.content || 'Template tidak ditemukan'}
            </div>
          </div>

          <div>
            <label className="form-label">
              Pilih Grup Target ({sendData.selected_groups.length} dari {groups.length} grup)
            </label>
            <div className="max-h-48 overflow-y-auto border rounded-lg">
              {groups.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  Tidak ada grup aktif tersedia
                </div>
              ) : (
                <div className="p-2 space-y-1">
                  <div className="flex items-center space-x-2 p-2 border-b">
                    <input
                      type="checkbox"
                      checked={sendData.selected_groups.length === groups.length}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSendData({
                            ...sendData,
                            selected_groups: groups.map(g => g.group_id)
                          });
                        } else {
                          setSendData({
                            ...sendData,
                            selected_groups: []
                          });
                        }
                      }}
                      className="rounded border-gray-300"
                    />
                    <label className="font-medium text-sm">Pilih Semua</label>
                  </div>
                  
                  {groups.map((group) => (
                    <div key={group.id} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={sendData.selected_groups.includes(group.group_id)}
                        onChange={() => toggleGroupSelection(group.group_id)}
                        className="rounded border-gray-300"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-sm">{group.name || 'Tidak ada nama'}</div>
                        <div className="text-xs text-gray-500">
                          {group.username ? `@${group.username}` : `ID: ${group.group_id}`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                name="send_mode"
                checked={sendData.send_immediately}
                onChange={() => setSendData({...sendData, send_immediately: true})}
                className="rounded-full border-gray-300"
              />
              <span className="text-sm">Kirim Sekarang</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                name="send_mode"
                checked={!sendData.send_immediately}
                onChange={() => setSendData({...sendData, send_immediately: false})}
                className="rounded-full border-gray-300"
              />
              <span className="text-sm">Jadwalkan untuk Nanti</span>
            </label>
          </div>

          <div className="flex space-x-3 pt-4">
            <button 
              type="submit" 
              className="btn-primary flex-1"
              disabled={sendData.selected_groups.length === 0}
            >
              {sendData.send_immediately ? 'Kirim Sekarang' : 'Jadwalkan Pesan'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowSendModal(false);
                setSendData({ template_id: '', selected_groups: [], send_immediately: true });
              }}
              className="btn-secondary"
            >
              Batal
            </button>
          </div>
        </form>
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
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Template Pesan</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Kelola template pesan untuk pengiriman otomatis
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Template Baru
        </button>
      </div>

      {/* Templates List */}
      <div className="dashboard-card">
        {templates.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
              Belum ada template pesan
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Buat template pertama Anda untuk mulai mengirim pesan otomatis.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              Buat Template Pertama
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {templates.map((template) => (
              <div key={template.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center space-x-3">
                    <h3 className="font-semibold text-lg">{template.name}</h3>
                    {template.is_default && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        Default
                      </span>
                    )}
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => openSendModal(template.id)}
                      className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600 transition-colors"
                      title="Kirim pesan"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleEditTemplate(template)}
                      className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                      title="Edit template"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDeleteTemplate(template.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
                      title="Hapus template"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <p className="text-gray-700 whitespace-pre-wrap">{template.content}</p>
                </div>
                
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>{template.content.length} karakter</span>
                  <span>
                    Dibuat: {new Date(template.created_at).toLocaleDateString('id-ID')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      {showAddModal && <TemplateModal />}
      {showSendModal && <SendModal />}
    </div>
  );
};

export default MessageTemplates;