# 🚀 Telegram Auto Sender Backend V2.0

Modern FastAPI backend with Clean Architecture, built with 2025 best practices.

## 🏗️ Architecture

This backend follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── domain/              # Business Logic Layer
│   ├── entities/       # Domain entities with business rules
│   ├── repositories/   # Repository interfaces (abstractions)
│   └── services/       # Domain services
├── application/        # Application Layer
│   └── use_cases/     # Application business logic
└── infrastructure/    # Infrastructure Layer
    ├── database/      # Database implementations
    └── web/           # Web framework, API routes & dependencies
```

## 🛠️ Technologies

- **FastAPI** - Modern, fast web framework
- **Pydantic V2** - Data validation & serialization
- **Motor** - Async MongoDB driver
- **PyJWT** - JWT authentication
- **Uvicorn** - ASGI server
- **Clean Architecture** - Domain-driven design patterns

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the server:**
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/api/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Configuration

Key environment variables:

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=telegram_auto_sender_v2

# Security
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-encryption-key

# CORS & Security
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh-api-token` - Refresh API token

### Telegram Endpoints
- `POST /api/telegram/sessions` - Create Telegram session
- `POST /api/telegram/sessions/authenticate` - Authenticate session
- `GET /api/telegram/sessions` - Get user sessions
- `DELETE /api/telegram/sessions/{session_id}` - Delete session

### Group Management
- `POST /api/groups/single` - Add single group
- `POST /api/groups/bulk` - Bulk add groups
- `GET /api/groups` - List groups
- `GET /api/groups/stats` - Group statistics

## 🏛️ Clean Architecture Benefits

### Domain Layer
- **Pure business logic** - No external dependencies
- **Rich domain models** - Entities with behavior
- **Interface segregation** - Clear contracts

### Application Layer
- **Use cases** - Single responsibility operations
- **Command/Query separation** - Clear input/output
- **Cross-cutting concerns** - Logging, validation

### Infrastructure Layer
- **Dependency inversion** - Abstractions over implementations
- **Easy testing** - Mock repositories & services
- **Technology agnostic** - Switch databases/frameworks easily

## 🔒 Security Features

- **JWT Authentication** with proper expiration
- **Password hashing** with salt
- **Input validation** with Pydantic schemas
- **CORS protection** with configurable origins
- **Request logging** for monitoring
- **Error sanitization** - No internal details exposed

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

Test structure:
- **Unit tests** - Domain entities & services
- **Integration tests** - Use cases & repositories
- **API tests** - Endpoint behavior
- **Database tests** - Repository implementations

## 📊 Monitoring

### Health Checks
- `GET /health` - Application health status
- Includes database connectivity
- Performance metrics ready

### Logging
- **Structured logging** with JSON format
- **Correlation IDs** for request tracing
- **Performance timing** middleware
- **Error tracking** ready

## 🚀 Production Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Environment Setup
- Set `ENV=production`
- Configure proper `JWT_SECRET`
- Set up database connection
- Configure CORS origins
- Enable HTTPS

## 🔄 Migration from V1

The new architecture is designed for easy migration:

1. **Database compatibility** - Same schema, improved queries
2. **API compatibility** - Similar endpoints, enhanced responses
3. **Feature parity** - All V1 features implemented
4. **Performance improvements** - Async operations, better patterns

## 📈 Performance

- **Async/await** throughout for non-blocking operations
- **Connection pooling** with Motor
- **Request timing** middleware
- **Efficient serialization** with Pydantic V2
- **Ready for caching** layers

## 🔮 Future Enhancements

Ready for:
- **Microservices** split
- **Event-driven** architecture
- **CQRS** implementation
- **GraphQL** API layer
- **Real-time** WebSocket support

---

Built with ❤️ using modern Python best practices