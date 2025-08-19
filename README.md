# 🤖 Telegram Auto Sender

Aplikasi fullstack untuk mengirim pesan Telegram secara otomatis ke multiple groups dengan fitur advanced scheduling, blacklist management, monitoring real-time, dan session persistence.

## ✨ Fitur Utama

- 🔐 **Authentication System** - Login dengan Telegram API ID/Hash, support 2FA
- 🔄 **Auto-Login & Session Persistence** - Session tersimpan otomatis, tidak perlu login ulang
- 👥 **Group Management** - CRUD operations untuk groups Telegram dengan bulk add
- 📝 **Message Templates** - Sistem template pesan dengan default template
- 🚀 **Auto Message Sender** - Kirim pesan otomatis ke multiple groups
- ⏰ **Smart Scheduler** - Jadwal pengiriman dengan random intervals dan Telethon best practices
- 🚫 **Blacklist Management** - Sistem blacklist otomatis (temporary & permanent)
- 📊 **Dashboard & Monitoring** - Real-time statistics dan live activity logs
- 📡 **Live Activity Log** - Monitor aktivitas scheduler secara real-time
- ⚙️ **Settings Management** - Konfigurasi intervals, retry attempts, tema
- 🔄 **Real-time Updates** - Socket.IO untuk notifikasi dan progress updates

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: React + Tailwind CSS + Socket.IO Client
- **Database**: MongoDB
- **Real-time**: Socket.IO
- **Telegram API**: Telethon (with best practices)
- **Scheduler**: APScheduler
- **Session Storage**: Encrypted session storage with localStorage persistence

## 🚀 Cara Menggunakan

### 1. **Akses Aplikasi**
- Buka: https://fix-all-issues.preview.emergentagent.com
- Aplikasi akan otomatis login jika session masih valid

### 2. **Dapatkan API Credentials**
- Kunjungi: https://my.telegram.org/apps
- Buat aplikasi baru untuk mendapat API ID dan Hash
- Login dengan developer account Telegram Anda

### 3. **Login ke Telegram**
- Masukkan API ID dan API Hash
- Masukkan nomor telepon (+62xxx)
- Verifikasi dengan kode 5 digit dari Telegram
- Jika ada 2FA, masukkan password two-factor authentication
- ✅ Session akan tersimpan otomatis untuk login berikutnya

### 4. **Setup Template Pesan**
- Buka menu "Template Pesan" 
- Buat template baru dengan tombol "Template Baru"
- ⚠️ **PENTING**: Centang "Set as Default Template"
- Scheduler memerlukan default template untuk berfungsi

### 5. **Tambah Groups Target**
- Buka menu "Grup"
- Gunakan "Bulk Add" untuk menambah banyak grup sekaligus
- Format yang didukung:
  - Username: `@groupname`
  - Chat ID: `-1001234567890`
  - Invite Link: `https://t.me/+xxxxxx`

### 6. **Mulai Auto Sender**
- Kembali ke Dashboard
- Klik tombol "Start Scheduler"
- ✅ Scheduler akan mulai cycle pertama immediately
- Monitor aktivitas di "Live Activity Log"

## 📊 Dashboard Features

### Statistics Cards
- **Total Grup**: Jumlah grup yang ditambahkan
- **Grup Aktif**: Grup yang available untuk pengiriman
- **Pesan Terkirim**: Statistik 24 jam terakhir
- **Pesan Gagal**: Error rate dan troubleshooting

### Live Activity Log 
- **Real-time monitoring**: Aktivitas scheduler live
- **Cycle tracking**: Status setiap cycle pengiriman
- **Progress updates**: Progress per grup dan delay timing
- **Color-coded logs**: Info (blue), Success (green), Warning (yellow), Error (red)
- **Auto-refresh**: Update otomatis via Socket.IO

### Scheduler Controls
- **Start/Stop**: Control scheduler dengan immediate execution
- **Status indicator**: Visual status aktif/non-aktif
- **Group availability**: Monitor grup yang tersedia

## 🔧 Perbaikan Terbaru

### ✅ Auto-Login & Session Persistence
- **Problem**: Setiap refresh browser kembali ke halaman login
- **Solution**: Session tersimpan di localStorage dengan auto-validation
- **Benefit**: User experience yang seamless, tidak perlu login berulang

### ✅ Live Activity Monitoring 
- **Problem**: Tidak ada visibilitas real-time aktivitas scheduler
- **Solution**: Live log dashboard dengan Socket.IO integration
- **Benefit**: Monitor langsung aktivitas, debugging, dan troubleshooting

### ✅ Scheduler Optimization
- **Telethon Best Practices**: Message intervals 20-30 detik
- **Immediate Execution**: Cycle pertama langsung dijalankan
- **Smart Error Handling**: FloodWait, SlowMode, UserBanned detection
- **Real-time Updates**: Progress dan status via Socket.IO

## 🚨 Troubleshooting

### Scheduler Tidak Mengirim Pesan
**Root Cause**: Scheduler memerlukan 3 komponen:

1. **✅ Session Telegram Valid**
   - Login dengan API ID/Hash yang benar
   - Verifikasi nomor telepon dan 2FA

2. **✅ Default Template**
   - Buat minimal 1 template pesan
   - Set sebagai "Default Template" ⚠️

3. **✅ Grup Aktif** 
   - Tambahkan minimal 1 grup target
   - Pastikan grup accessible dan tidak di-blacklist

### Session Issues
- **Session Expired**: Akan otomatis clear dan redirect ke login
- **Invalid Credentials**: Check API ID/Hash di my.telegram.org
- **Network Issues**: Check koneksi internet dan firewall

### Group Management
- **Grup Tidak Ditemukan**: Check username/ID/link format
- **Akses Ditolak**: Pastikan bot/user ada di grup
- **Blacklist**: Check status grup di dashboard

## 📁 Struktur Project

```
/app/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main application dengan Socket.IO
│   ├── requirements.txt    # Dependencies (+ tzlocal, socketio)
│   └── .env               # MongoDB URL dan encryption key
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginPage.js      # Auto-login support
│   │   │   ├── Dashboard.js      # Live log integration
│   │   │   ├── GroupManager.js   # Bulk add functionality
│   │   │   ├── MessageTemplates.js
│   │   │   ├── Settings.js
│   │   │   └── Navigation.js
│   │   ├── App.js              # Session persistence logic
│   │   └── App.css            # Tailwind styling
│   ├── package.json           # Socket.IO client dependency
│   └── .env                  # Backend URL configuration
├── test_result.md            # Comprehensive testing documentation
└── comprehensive_scheduler_test.py  # Advanced testing suite
```

## ⚙️ Settings & Configuration

### Message Intervals (Telethon Best Practices)
- **Min Interval**: 20 detik (mencegah FloodWaitError)
- **Max Interval**: 30 detik (optimal performance)
- **Cycle Intervals**: 60-120 menit (randomized)

### Advanced Features
- **Smart Blacklist**: Auto-blacklist temporary (FloodWait) dan permanent (UserBanned)
- **Session Encryption**: AES-256 encryption untuk session storage
- **Real-time Sync**: Socket.IO untuk updates langsung
- **Error Recovery**: Automatic retry dengan exponential backoff

## 🔒 Security Features

- **Encrypted Sessions**: Session Telegram dienkripsi AES-256
- **Secure Storage**: Sensitive data di database terenkripsi
- **Auto Logout**: Invalid session otomatis logout
- **CORS Protection**: API endpoints dengan proper CORS
- **Input Validation**: Comprehensive input sanitization

## 📈 Performance & Monitoring

### Real-time Metrics
- **Success Rate**: Persentase pengiriman berhasil
- **Group Status**: Active, temporary blacklist, permanent blacklist
- **Message Statistics**: Sent vs failed dengan breakdown 24 jam
- **Scheduler Performance**: Cycle timing dan execution logs

### Socket.IO Events
- `scheduler_status`: Status cycle (started, completed, scheduled)
- `sending_progress`: Progress pengiriman per grup
- `sending_delay`: Countdown delay antar pesan
- `message_results`: Hasil batch pengiriman

## 🎯 Best Practices

### Untuk Menghindari Rate Limiting
1. **Gunakan interval 20-30 detik** antar pesan
2. **Jangan kirim ke terlalu banyak grup** dalam satu cycle
3. **Monitor blacklist status** dan bersihkan berkala
4. **Gunakan template yang tidak spam** untuk menghindari report

### Untuk Performance Optimal
1. **Set default template** sebelum mulai scheduler
2. **Tambah grup secara bertahap** untuk testing
3. **Monitor live logs** untuk troubleshooting
4. **Update settings** sesuai kebutuhan network

---

**🚀 Ready to Use**: Aplikasi siap digunakan dengan semua fitur yang sudah dioptimasi
**📞 Support**: Gunakan live log untuk troubleshooting real-time
**⭐ Enhanced UX**: Auto-login, session persistence, dan real-time monitoring

**Dibuat dengan ❤️ menggunakan FastAPI, React, Socket.IO, dan Telethon**