# 🤖 Telegram Auto Sender

Aplikasi fullstack untuk mengirim pesan Telegram secara otomatis ke multiple groups dengan fitur advanced scheduling, blacklist management, dan monitoring.

## ✨ Fitur Utama

- 🔐 **Authentication System** - Login dengan Telegram API ID/Hash, support 2FA
- 👥 **Group Management** - CRUD operations untuk groups Telegram
- 📝 **Message Templates** - Sistem template pesan dengan default template
- 🚀 **Auto Message Sender** - Kirim pesan otomatis ke multiple groups
- ⏰ **Smart Scheduler** - Jadwal pengiriman dengan random intervals
- 🚫 **Blacklist Management** - Sistem blacklist otomatis (temporary & permanent)
- 📊 **Dashboard & Monitoring** - Real-time statistics dan message logs
- ⚙️ **Settings Management** - Konfigurasi intervals, retry attempts, tema
- 🔄 **Real-time Updates** - Socket.IO untuk notifikasi real-time

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: React + Tailwind CSS
- **Database**: MongoDB
- **Cache**: Redis
- **Real-time**: Socket.IO
- **Telegram API**: Telethon
- **Scheduler**: APScheduler

## 🚀 Cara Menggunakan

1. **Buka aplikasi**: https://telegram-bot-auto.preview.emergentagent.com

2. **Dapatkan API Credentials**:
   - Kunjungi: https://my.telegram.org/apps
   - Buat aplikasi baru untuk mendapat API ID dan Hash

3. **Login**:
   - Masukkan API ID dan API Hash
   - Masukkan nomor telepon
   - Verifikasi dengan kode yang diterima
   - Jika ada 2FA, masukkan password

4. **Kelola Groups**:
   - Tambah groups Telegram yang ingin dikirimi pesan
   - Monitor status groups (active/blacklisted)

5. **Buat Templates**:
   - Buat template pesan yang akan dikirim
   - Set template default untuk auto sender

6. **Kirim Pesan**:
   - Kirim manual atau schedule otomatis
   - Monitor hasil pengiriman di dashboard

## 📁 Struktur Project

```
/app/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main application file
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── App.js         # Main app component
│   │   └── App.css        # Styling
│   ├── package.json       # Node dependencies
│   └── .env              # Frontend environment
├── test_result.md         # Testing documentation
└── backend_test.py        # Backend API tests
```

## 🔧 Fitur Advanced

### Smart Blacklist System
- **FloodWaitError**: Temporary blacklist dengan countdown
- **SlowModeWaitError**: Skip untuk cycle saat ini
- **UserBannedError**: Permanent blacklist
- **Auto cleanup**: Blacklist temporary dibersihkan setiap cycle

### Intelligent Scheduler
- **Random intervals**: Hindari deteksi bot
- **Retry logic**: Auto retry dengan exponential backoff
- **Group availability**: Hanya kirim ke groups yang available
- **Real-time monitoring**: Monitor status via Socket.IO

### Security Features
- **Session encryption**: Session Telegram dienkripsi sebelum disimpan
- **Secure authentication**: Proper 2FA handling
- **Error handling**: Comprehensive error handling dan logging

## 📊 Monitoring & Analytics

- **Dashboard statistics**: Total groups, messages sent/failed, scheduler status
- **Message logs**: Detailed logs setiap pengiriman pesan
- **Group analytics**: Statistics per group dan status tracking
- **Real-time updates**: Live notifications via Socket.IO

## ⚙️ Konfigurasi

Aplikasi dapat dikonfigurasi melalui Settings page:
- **Message intervals**: Min/max delay antar pesan
- **Cycle intervals**: Min/max delay antar cycle
- **Retry attempts**: Jumlah maksimal retry
- **Theme**: Light/dark mode
- **Notifications**: Enable/disable notifications

---

**Dibuat dengan ❤️ menggunakan FastAPI, React, dan Telethon**