# 🚀 Telegram Auto Sender V2.0

Modern fullstack application for Telegram automation with **Clean Architecture**, **TypeScript**, and **2025 best practices**.

## 🏗️ Project Structure

```
/app/
├── backend/                    # FastAPI + Clean Architecture
├── frontend/                   # React + TypeScript + Vite
├── backup_old_version/         # Archived legacy code
└── REFACTORED_PROJECT_SUMMARY.md
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** 
- **Yarn**
- **MongoDB**

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python main.py
```

### Frontend Setup  
```bash
cd frontend
yarn install
cp .env.example .env.local
# Edit .env.local with backend URL
yarn dev
```

### Full Development
```bash
# Terminal 1 - Backend (Port 8001)
cd backend && python main.py

# Terminal 2 - Frontend (Port 3000)
cd frontend && yarn dev
```

## 🎯 Technology Stack

### Backend
- ✅ **FastAPI** - Modern Python web framework
- ✅ **Clean Architecture** - Domain-driven design
- ✅ **Pydantic V2** - Data validation
- ✅ **MongoDB** - Document database
- ✅ **JWT** - Authentication

### Frontend  
- ✅ **React 18** - Modern React with hooks
- ✅ **TypeScript** - Type safety
- ✅ **Vite** - Fast build tool
- ✅ **Zustand** - State management
- ✅ **Tailwind CSS** - Utility styling
- ✅ **shadcn/ui** - Component library

## 📚 Documentation

- **[Backend Documentation](./backend/README.md)** - FastAPI setup & architecture
- **[Frontend Documentation](./frontend/README.md)** - React setup & components
- **[Refactoring Summary](./REFACTORED_PROJECT_SUMMARY.md)** - Complete transformation details

## 🎉 What's New in V2.0

### 🏛️ Architecture Improvements
- **Clean Architecture** with domain-driven design
- **Repository Pattern** for data abstraction
- **Use Cases** for business logic
- **Dependency Injection** throughout

### 💻 Development Experience
- **100% TypeScript** frontend
- **Type-safe** API communication
- **Hot reload** for instant feedback
- **Modern tooling** (Vite, ESLint, Prettier)

### 🎨 User Experience
- **Modern UI** with shadcn/ui components
- **Dark/Light theme** support
- **Responsive design** for all devices
- **Better performance** with modern patterns

### 🔒 Security & Quality
- **Enhanced authentication** with JWT
- **Input validation** with Pydantic & Zod
- **Error boundaries** for graceful failures
- **Production-ready** monitoring hooks

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login  
- `GET /api/auth/me` - Current user info

### Telegram Management
- `POST /api/telegram/sessions` - Create session
- `GET /api/telegram/sessions` - List sessions
- `POST /api/telegram/sessions/authenticate` - Authenticate

### Group Management
- `POST /api/groups/single` - Add group
- `POST /api/groups/bulk` - Bulk add groups
- `GET /api/groups` - List groups

## 📱 Features

- ✅ **User Authentication** - Secure login/registration
- ✅ **Telegram Integration** - Session management
- ✅ **Group Management** - Add/manage groups
- ✅ **Message Templates** - Reusable messages
- ✅ **Dashboard** - Statistics & overview
- ✅ **Settings** - User preferences
- ✅ **Responsive Design** - Mobile-friendly

## 🔧 Environment Configuration

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=telegram_auto_sender
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8001/api
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
yarn test
```

## 📦 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
1. Build frontend: `cd frontend && yarn build`
2. Configure production environment variables
3. Deploy backend to cloud provider
4. Serve frontend static files

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using modern fullstack development practices**