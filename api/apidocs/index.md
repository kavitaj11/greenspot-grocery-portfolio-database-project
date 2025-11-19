# 📚 Greenspot Grocer API Documentation

Welcome to the comprehensive documentation for the Greenspot Grocer Analytics API!

## 📖 Documentation Structure

### Core Documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Get started quickly with the API
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Complete JWT authentication guide
- **[SECURITY.md](SECURITY.md)** - Security features and encryption details
- **[README.md](README.md)** - Main API documentation and overview

## 🚀 Quick Navigation

### Getting Started
1. **First Time Setup**: Read [QUICKSTART.md](QUICKSTART.md)
2. **Authentication Guide**: Learn [AUTHENTICATION.md](AUTHENTICATION.md)
3. **Security Configuration**: Review [SECURITY.md](SECURITY.md)
4. **Complete API Reference**: Check [README.md](README.md)

### For Developers
- **API Endpoints**: Check [README.md](README.md) for endpoint details
- **Authentication Setup**: Follow [AUTHENTICATION.md](AUTHENTICATION.md) for JWT setup
- **Testing**: Use scripts in `/tests/` folder
- **Configuration**: Modify files in `/config/` folder
- **Utilities**: Use tools in `/utils/` folder

## 🔗 External Documentation
- **Interactive API Docs**: `http://localhost:8000/docs` (when API is running)
- **Alternative API Docs**: `http://localhost:8000/redoc` (when API is running)

## 📁 Project Structure Overview

```
api/
├── apidocs/                   # 📚 API Documentation
│   ├── __init__.py
│   ├── index.md              # This file - Documentation index
│   ├── QUICKSTART.md         # Quick start guide
│   ├── AUTHENTICATION.md     # JWT authentication guide
│   ├── SECURITY.md           # Security and encryption
│   └── README.md             # Complete API reference
├── config/                    # ⚙️ Configuration
│   ├── __init__.py           # Encrypted configuration
│   └── .env.template         # Environment variables
├── utils/                     # 🛠️ Utilities
│   ├── encryption_utils.py   # Password encryption
│   └── password_manager.py   # Password management
├── tests/                     # 🧪 Testing
│   ├── simple_test_runner.py # Test runner
│   ├── db_test.py            # Database tests
│   └── schema_check.py       # Schema validation
├── models.py                  # Pydantic data models
├── endpoints.py               # API endpoints (legacy)
└── main.py                    # 🚀 Main API application
```

## 🎯 Documentation Standards

### File Naming Convention
- `README.md` - Main project documentation and API reference
- `QUICKSTART.md` - Getting started guide for new users
- `AUTHENTICATION.md` - Complete JWT authentication documentation
- `SECURITY.md` - Security features and encryption details

### Documentation Types
- **User Guides** - For API consumers and users
- **Developer Guides** - For contributors and maintainers
- **Security Guides** - For security configuration and best practices
- **API Reference** - Interactive documentation via Swagger/OpenAPI

## 🔄 Keeping Documentation Updated

When making changes to the API:
1. Update relevant documentation files
2. Verify all links and references work
3. Test code examples in documentation
4. Update version numbers where applicable

## 🚦 API Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Main API** | ✅ Operational | `python main.py` |
| **Database** | ✅ Connected | MySQL with encrypted passwords |
| **Authentication** | ✅ Active | JWT with 30-min expiration |
| **Testing Suite** | ✅ Passing | All tests operational |
| **Documentation** | ✅ Complete | Interactive docs at `/docs` |

## 🔗 Quick Links

### Testing the API
```bash
# Start the API
cd api
python main.py

# Run tests
python tests/simple_test_runner.py

# Access interactive docs
# Visit: http://127.0.0.1:8000/docs
```

### Authentication Quick Test
```bash
# Login (get token)
curl -X POST "http://127.0.0.1:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'

# Use token for protected endpoint
curl -X GET "http://127.0.0.1:8000/executive-summary" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Available Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | ❌ | API information |
| `/health` | GET | ❌ | Health check |
| `/login` | POST | ❌ | Get JWT token |
| `/executive-summary` | GET | ✅ | Business metrics |
| `/product-performance` | GET | ✅ | Product analytics |
| `/customer-insights` | GET | ✅ | Customer data |
| `/inventory-status` | GET | ✅ | Inventory levels |

## 📞 Support

For questions or issues:
1. **Documentation**: Check the files in this folder
2. **Interactive Testing**: Visit `http://127.0.0.1:8000/docs`
3. **Testing**: Run `python tests/simple_test_runner.py`
4. **Configuration**: Review files in `/config/` folder
5. **Authentication**: See [AUTHENTICATION.md](AUTHENTICATION.md)

## 🎉 Ready to Use!

Your Greenspot Grocer Analytics API is fully documented and ready for:
- **Development**: Local testing and integration
- **Production**: Secure deployment with encrypted passwords
- **Integration**: Complete authentication and endpoint documentation
- **Maintenance**: Comprehensive testing and monitoring tools

---

**Last Updated**: November 2025 | **API Version**: 2.1.0

**Happy coding with the Greenspot Grocer API! 🛒✨**